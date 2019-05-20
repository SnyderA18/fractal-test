import arcade
import PIL
import PIL.Image
import random


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Fractal Drawer"

try:
    from numba import jit
    HASNUMBA=True
except ImportError:
    HASNUMBA=False


def _mandel_core(c, maxIter):
    z=0+0j
    for i in range(maxIter):
        z = z*z + c
        if z.real * z.real + z.imag * z.imag > 4:
            break
    return i


mandle_core = _mandel_core
if HASNUMBA:
    mandle_core = jit(_mandel_core,nopython=True)
    # mandle_core = dispatcher(_mandel_core, nopython=True)
    mandle_core.compile('uint(complex64,uint8)')
    

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


    def on_draw(self):
        arcade.start_render()
        self.background_sprite.draw()
        
    @jit
    def update(self, delta_time):
        # Number of lines to draw per update cycle
        lines = 20
        if self.y >= SCREEN_HEIGHT:
            self.on_close()
            return
        for _ in range(lines):
            cy = self.y * (self.ymax - self.ymin) / (SCREEN_HEIGHT - 1) + self.ymin
            for x in range(SCREEN_WIDTH):
                cx = x * (self.xmax - self.xmin) / (SCREEN_WIDTH - 1) + self.xmin
                c = complex(cx, cy)
                z = 0+0j
                i = mandle_core(c, self.maxIter)
                if i >= self.maxIter - 1:
                    color = 0
                else:
                    color = (i << 21) + (i << 10) + i*8
                self.bitmap[x, self.y] = color
            self.y += 1

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
