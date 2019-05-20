import arcade
import PIL
import PIL.Image
import random

import multiprocessing as mp
from multiprocessing import Pool, Array
import SharedArray
import numpy

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Fractal Drawer"

try:
    from numba import jit
    HASNUMBA=True
except ImportError:
    HASNUMBA=False

# HASNUMBA=False
def _mandel_core(c, maxIter):
    z=0+0j
    for i in range(maxIter):
        z = z*z + c
        if z.real * z.real + z.imag * z.imag > 4:
            break
    return i


mandle_core = _mandel_core
if HASNUMBA:
    mandel_core = jit(_mandel_core,nopython=True)

def mandel(min, max, iter, width, height, buffer):
    for y in height:
        cy = min.imag * (max.imag - min.imag) / (width - 1) + min.imag
        for x in width:
            cx = min.real * (max.real - min.real) / (height - 1) + min.real
            c = complex(cx, cy)
            i = mandel_core(c, iter)
            if i >= iter - 1:
                    color = 0
            else:
                color = (i << 21) + (i << 10) + i*8
            buffer[x, y] = color
    return (x,y,buffer)



class MyGame(arcade.Window):
    """
    Main application class.

    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        
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
        arcade.set_background_color(arcade.color.AMAZON)
        # Create your sprites and sprite lists here
        self.off_screen_image = PIL.Image.new("RGB", (SCREEN_WIDTH, SCREEN_HEIGHT), arcade.color.AMAZON)
        self.bitmap = self.off_screen_image.load()  # Load the image into a writable byte object
        
        self.texture = arcade.Texture('background', self.off_screen_image)
        self.background_sprite = arcade.Sprite()
        self.background_sprite.center_x = SCREEN_WIDTH // 2
        self.background_sprite.center_y = SCREEN_HEIGHT // 2
        self.background_sprite.texture = self.texture

        self.y = 0
        self.xmin = -2.0
        self.xmax = 1.0
        self.ymin = -1.5
        self.ymax = 1.5
        self.min = complex(self.xmin, self.ymin)
        self.max = complex(self.xmax, self.ymax)
        self.divisions = 16
        self.results = None
        divisions = self.divisions
        buffer = numpy.mgrid[self.xmin:self.xmax:SCREEN_WIDTH*1j, self.ymin:self.ymax:SCREEN_HEIGHT*1j].reshape(2,-1).T
       
    def on_draw(self):
        arcade.start_render()
        self.background_sprite.draw()
        
    @jit
    def update(self, delta_time):
        update_texture = False
        completed_results = []
        for r in self.results:
            if r.ready():
                    print("Ready process", r)
                #if r.successful():
                    print("It was successful")
                    completed_results.append(r)
                    x,y,buffer = r.get()
                    print(x,y,buffer)
                    print(buffer)
                    tile_image = PIL.Image.fromarray(buffer,"RGB")
                    self.off_screen_image.paste(tile_image,x,y)
                    update_texture = True

        if update_texture:
            # Convert the image to a texture
            self.texture = arcade.Texture('background', self.off_screen_image)
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

if __name__ == "__main__":
    main()
