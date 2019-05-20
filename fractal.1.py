import arcade
import PIL
import PIL.Image
import pyglet.app
import cmath
import random

import multiprocessing
from multiprocessing import Queue, Process
import queue

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"

from numba import jit

#@jit
def draw_julia(c, result_queue, command_queue, origin = (0,0), zoom = 1, maxIter = 128, width = SCREEN_WIDTH, height = SCREEN_HEIGHT):
    originX = origin[0]
    originY = origin[1]
    half_zoom_height = (0.5 * zoom * height)
    for y in range(height):
        zy = 1.0 * (y - width / 2) / half_zoom_height + originY 
        for x in range(width):
            zx = 1.5 * (x - width / 2) / half_zoom_height + originX 
    
            z = complex(zx, zy)
            i = maxIter 
            while abs(z) < 8 and i > 1:
                z = z * z + c
                i -= 1
                #print(z)
            color = (i << 21) + (i << 10) + i*8
            calc = (x, y, color)
            calc2 = (width - x - 1, height - y - 1, color)
            if result_queue.full():
                print("Queue full, blocking")
            while True:
                try:
                    # Check command queue before every calculation
                    try:
                        cmd = command_queue.get(False)
                        print("Got command of %s" % cmd)
                        if cmd == 'stop':
                            print("Stop command recieved")
                            return
                    except queue.Empty:
                        pass
                    result_queue.put(calc, False, 0.001)
                    #result_queue.put(calc2, False, 0.001)
                except queue.Full:
                    pass
                else:
                    break

#@jit
def mandel_core(c, maxIter):
    z=0+0j
    for i in range(maxIter):
        z = z*z + c
        if z.real * z.real + z.imag * z.imag > 4:
            break
    return i

@jit
def mandel_jit(c, maxIter):
    z=0+0j
    for i in range(maxIter):
        z = z*z + c
        if z.real * z.real + z.imag * z.imag > 4:
            break
    return i

def draw_mandlebrot(c, result_queue, command_queue, origin = (0,0), zoom = 1, maxIter = 128, width = SCREEN_WIDTH, height = SCREEN_HEIGHT):
    originX = origin[0]
    originY = origin[1]
    xmin = -2.0
    ymin = -1.5
    xmax = 1
    ymax = 1.5
    half_zoom_height = (0.5 * zoom * height)
    for y in range(height):
        #cy = 1.0 * (y - width / 2) / half_zoom_height + originY 
        cy = y * (ymax - ymin) / (height - 1) + ymin
        for x in range(width):
            #cx = 1.5 * (x - width / 2) / half_zoom_height + originX 
            cx = x * (xmax - xmin) / (width - 1) + xmin
    
            c = complex(cx, cy)
            z = 0+0j
            i = mandel_core(c, maxIter)
            color = (i << 21) + (i << 10) + i*8
            calc = (x, y, color)
            calc2 = (width - x - 1, height - y - 1, color)
            if result_queue.full():
                print("Queue full, blocking")
            while True:
                try:
                    # Check command queue after every calculation
                    try:
                        cmd = command_queue.get(False)
                        print("Got command of %s" % cmd)
                        if cmd == 'stop':
                            print("Stop command recieved")
                            return
                    except queue.Empty:
                        pass
                    result_queue.put(calc, False, 0.001)
                    #result_queue.put(calc2, False, 0.001)
                except queue.Full:
                    pass
                else:
                    break

class MyGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)
        self.origin = (0.0, 0.0)
        self.c = complex(0.27015, -0.7)
        self.c = complex(random.randrange(-1, 1), random.randrange(-1, 1))
        self.maxIter = 255
        self.zoom = 1
        self.x = 0
        self.y = 0
        self.color = 0
        # If you have sprite lists, you should create them here,
        # and set them to None

    def setup(self):
        # Create your sprites and sprite lists here
        self.off_screen_image = PIL.Image.new("RGB", (SCREEN_WIDTH, SCREEN_HEIGHT), (128,128,128))
        self.bitmap = self.off_screen_image.load()  # Load the image into a writable byte object
        
        self.texture = arcade.Texture('background', self.off_screen_image)
        self.background_sprite = arcade.Sprite()
        self.background_sprite.center_x = SCREEN_WIDTH // 2
        self.background_sprite.center_y = SCREEN_HEIGHT // 2
        self.background_sprite.texture = self.texture
        self.result_queue = Queue(5000)
        self.command_queue = Queue(5)
        #p = Process(target=draw_julia, args=(self.c, self.result_queue, self.command_queue, self.origin, self.zoom, self.maxIter,SCREEN_WIDTH,SCREEN_HEIGHT))
        draw_mandlebrot
        p = Process(target=draw_mandlebrot, args=(self.c, self.result_queue, self.command_queue, self.origin, self.zoom, self.maxIter,SCREEN_WIDTH,SCREEN_HEIGHT))
        p.start()


    def on_draw(self):
        arcade.start_render()
        self.background_sprite.draw()
        

    def update(self, delta_time):
        max_items = 2000 # Maximum items to dequeue at once
        # Read items out of the result queue
        for i in range(max_items):
            try:
                x, y, color = self.result_queue.get(False)
                # print(x,y,color)
                self.bitmap[x, y] = color
            except queue.Empty:
                #print("Queue was empty")
                break
        self.texture = arcade.Texture('background', self.off_screen_image)
        self.background_sprite.texture = self.texture

    def on_close(self):
        print("Got window close event")
        self.command_queue.put('stop', False)
        super().on_close()

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        pass

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
        pass


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

#def draw_mandlebrot(c, result_queue, command_queue, origin = (0,0), zoom = 1, maxIter = 128, width = SCREEN_WIDTH, height = SCREEN_HEIGHT):
def benchmark_mandel(core, c):
    # originX = 0
    # originY = 0
    # xmin = -2.0
    # ymin = -1.5
    # xmax = 1
    # ymax = 1.5
    core(c,255)
    # height = SCREEN_HEIGHT
    # width = SCREEN_WIDTH
    # zoom = 1.5
    # maxIter = 255
    # half_zoom_height = (0.5 * zoom * height)
    # for y in range(height):
    #     #cy = 1.0 * (y - width / 2) / half_zoom_height + originY 
    #     cy = y * (ymax - ymin) / (height - 1) + ymin
    #     for x in range(width):
    #         #cx = 1.5 * (x - width / 2) / half_zoom_height + originX 
    #         cx = x * (xmax - xmin) / (width - 1) + xmin
    
    #         c = complex(cx, cy)
    #         z = 0+0j
    #         i = mandel_core(c, maxIter)

if __name__ == "__main__":
    #main()
    import timeit
    number = 1000 * 1000

    units = {"nsec": 1e-9, "usec": 1e-6, "msec": 1e-3, "sec": 1.0}
    precision = 3
    time_unit = None
    def format_time(dt):
        unit = time_unit

        if unit is not None:
            scale = units[unit]
        else:
            scales = [(scale, unit) for unit, scale in units.items()]
            scales.sort(reverse=True)
            for scale, unit in scales:
                if dt >= scale:
                    break
        return "%.*g %s" % (precision, dt / scale, unit)

    cx = random.random() * 3 - 2
    cy = random.random() * 3 - 1.5
    c = complex(cx, cy)

    print("Running standard test:")
    bare_time = timeit.timeit("benchmark_mandel(mandel_core,c)", globals=globals(), number = number)
    print("\tExecution took %f" % bare_time)
    avg_time = float(bare_time / number)
    print("\tAverage execution took", format_time(avg_time))
    
    print("Running JIT test:")
    bare_time = timeit.timeit("benchmark_mandel(mandel_jit,c)", globals=globals(), number = number)
    print("\tExecution took %f" % bare_time)
    avg_time = float(bare_time / number)
    print("\tAverage execution took", format_time(avg_time))
    