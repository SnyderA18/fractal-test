import arcade
import PIL
import PIL.Image
import random
import numpy as np
import threading
import multiprocessing
import time
from queue import Queue

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Fractal Drawer"

HASNUMBA=False
try:
    from numba import jit
    HASNUMBA=True
except ImportError:
    pass

HASPYXIMPORT=False

try:
    import pyximport; pyximport.install()
    HASPYXIMPORT=True
except ImportError:
    pass

def _mandel_core(c, maxIter):
    z=0+0j
    for i in range(maxIter):
        z = z*z + c
        if z.real * z.real + z.imag * z.imag > 4:
            break
    return i

mandle_core = _mandel_core
if HASPYXIMPORT:
    import cython_core
    mandle_core = cython_core.mandel_core_complex_double
    print("Using Cython core")
elif HASNUMBA:
    mandle_core = jit(_mandel_core,nopython=True)
    # mandle_core = dispatcher(_mandel_core, nopython=True)
    mandle_core.compile('uint(complex64,uint8)')
    

# def _draw_fractal(xmin, xmax, ymin, ymax, maxIter, xoffset, yoffset, width, height, buffer):
#     starttime = time.time()
#     ystep = (ymax - ymin) / (height - 1)
#     xstep = (xmax - xmin) / (width - 1)
#     for y in range(yoffset, yoffset + height):
#         cy = (y - yoffset) * ystep + ymin
#         for x in range(xoffset, xoffset + width):
#             cx = (x - xoffset) * xstep + xmin
#             # print("x,y =",(x,y), "cx,cy = (%0.4f,%0.4f)" % (cx,cy))
#             c = complex(cx, cy)
#             z = 0+0j
#             i = mandle_core(c, maxIter)
#             if i >= maxIter - 1:
#                 buffer[y,x] = 0
#             else:
#                 color = (i << 21) + (i << 10) + i*8
#                 buffer[y,x] = color
#     print("Calculation took %.2f seconds" % (time.time() - starttime))

def _draw_fractal_queue(command_queue, buffer):
    while True:
        message = command_queue.get()
        if message == "quit":
            return

        xmin, xmax, ymin, ymax, maxIter, xoffset, yoffset, width, height = message
        starttime = time.time()

        ystep = (ymax - ymin) / (height - 1)
        xstep = (xmax - xmin) / (width - 1)
        for y in range(yoffset, yoffset + height):
            cy = (y - yoffset) * ystep + ymin
            for x in range(xoffset, xoffset + width):
                cx = (x - xoffset) * xstep + xmin
                c = complex(cx, cy)
                z = 0+0j
                i = mandle_core(c, maxIter)
                if i >= maxIter - 1:
                    buffer[y,x] = 0
                else:
                    color = (i << 21) + (i << 10) + i*8
                    buffer[y,x] = color
        print("Calculation took %.2f seconds" % (time.time() - starttime))

draw_fractal = _draw_fractal_queue
if HASPYXIMPORT:
    draw_fractal = cython_core._draw_fractal_queue_double
    print("Using Cython draw_fractal")

class MyGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # If you have sprite lists, you should create them here,
        # and set them to None

    def setup(self):
        arcade.set_background_color(arcade.color.AMAZON)
        self.origin = (0.0, 0.0)
        self.c = complex(0.27015, -0.7)
        self.c = complex(random.randrange(-1, 1), random.randrange(-1, 1))
        self.maxIter = 255
        self.zoom = 1
        self.x = 0
        self.y = 0
        self.color = 0
        # Create your sprites and sprite lists here
        #self.data = np.ascontiguousarray(np.empty((SCREEN_HEIGHT,SCREEN_WIDTH,3),dtype=np.uint8), dtype=np.uint8)
        self.data = np.empty((SCREEN_HEIGHT,SCREEN_WIDTH),dtype=np.uint32)
        
        self.texture = arcade.Texture('background')
        self.background_sprite = arcade.Sprite()
        self.background_sprite.center_x = SCREEN_WIDTH // 2
        self.background_sprite.center_y = SCREEN_HEIGHT // 2
        self.background_sprite.texture = self.texture

        self.y = 0
        self.xmin = -2.0
        self.xmax = 1.0
        self.ymin = -1.5
        self.ymax = 1.5
        self.threads = []
        self.command_queue = Queue()
        self.divs = 16
        for i in range(multiprocessing.cpu_count()):
            t = threading.Thread(target=draw_fractal, args=(self.command_queue, self.data), daemon=True)
            t.start()
            self.threads.append(t)
        self.divide_drawing()

    def divide_drawing(self):
        div_per_axis = self.divs // 2
        div_width = SCREEN_WIDTH // div_per_axis
        div_height = SCREEN_HEIGHT // div_per_axis
        for y in range(div_per_axis):
            for x in range(div_per_axis):
                xmin = x * ((self.xmax - self.xmin) / div_per_axis) + self.xmin
                xmax = xmin + (self.xmax - self.xmin) / div_per_axis
                ymin = y * ((self.ymax - self.ymin) / div_per_axis) + self.ymin
                ymax = ymin + (self.ymax - self.ymin) / div_per_axis
                args=(xmin, xmax, ymin, ymax, self.maxIter, div_width * x, div_height * y, div_width, div_height)
                self.command_queue.put(args)

    def on_draw(self):
        arcade.start_render()
        self.background_sprite.draw()
        
    def _point_to_screen(self, cx, cy):
        x = ((cx - self.xmin) * (SCREEN_WIDTH - 1)) / (self.xmax - self.xmin)
        y = ((cy - self.ymin) * (SCREEN_HEIGHT - 1)) / (self.ymax - self.ymin)
        return x, SCREEN_HEIGHT - y

    def _screen_to_point(self, x, y):
        cy = (SCREEN_HEIGHT - y) * (self.ymax - self.ymin) / (SCREEN_HEIGHT - 1) + self.ymin
        cx = x * (self.xmax - self.xmin) / (SCREEN_WIDTH - 1) + self.xmin
        return cx, cy

    def update(self, delta_time):
        self.texture = arcade.Texture('background', PIL.Image.fromarray(self.data, mode='RGBX'))
        # Set the texture of the background sprite
        self.background_sprite.texture = self.texture

    def on_close(self):
        # print("Got window close event")
        # self.command_queue.put('stop', False)
        super().on_close()
        pass

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        if key == arcade.key.PLUS:
            self.maxIter = int(self.maxIter * 1.1)
            self._clear_image()
            self.y = 0
            print("New iterations:", self.maxIter)
        elif key == arcade.key.MINUS:
            self.maxIter = max(255, int(self.maxIter * 0.9))
            self._clear_image()
            self.y = 0
            print("New iterations:", self.maxIter)

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        print("before: (%0.4f,%0.4f)-(%0.4f,%0.4f)" % (self.xmin,self.ymin,self.xmax,self.ymax))
        # Zoom out if the shift key is pressed, in otherwise
        if key_modifiers & arcade.key.MOD_SHIFT == 1:
            # zooming out
            cur_width = self.xmax - self.xmin
            cur_height = self.ymax - self.ymin
            cx, cy = self._screen_to_point(x,y)
            self.xmin = cx - cur_width
            self.xmax = cx + cur_width
            self.ymin = cy - cur_height
            self.ymax = cy + cur_height
            self.y = 0
            self._clear_image()
        else:
            cur_width = self.xmax - self.xmin
            cur_height = self.ymax - self.ymin
            cx, cy = self._screen_to_point(x,y)
            self.xmin = cx - cur_width / 4
            self.xmax = cx + cur_width / 4
            self.ymin = cy - cur_height / 4
            self.ymax = cy + cur_height / 4
            self.y = 0
            self._clear_image()
        print("after: (%0.4f,%0.4f)-(%0.4f,%0.4f)" % (self.xmin,self.ymin,self.xmax,self.ymax))

    def _clear_image(self, color = arcade.color.AMAZON):
        #self.data = 
        self.divide_drawing()
        #self.off_screen_image.paste(color, (0,0,self.off_screen_image.size[0], self.off_screen_image.size[1]))



def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
