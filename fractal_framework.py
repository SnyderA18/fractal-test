import arcade
import PIL

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


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
        self.originX, self.originY = 0.0, 0.0
        self.cY, self.cX = 0.27015, -0.7
        self.maxIter =128
        self.zoom = 1.5
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
        self.y = 1

    def on_draw(self):
       
        arcade.start_render()
        self.background_sprite.draw()
        
        #print(self.x, self.y, self.color)
        

    def update(self, delta_time):
            self.zx = 1.5*(self.x - SCREEN_WIDTH/2)/(0.5*self.zoom*SCREEN_WIDTH) + self.originX 
            self.zy = 1.0*(self.y - SCREEN_HEIGHT/2)/(0.5*self.zoom*SCREEN_HEIGHT) + self.originY 
            i = self.maxIter 
            while self.zx*self.zx + self.zy*self.zy < 4 and i > 1: 
                tmp = self.zx*self.zx - self.zy*self.zy + self.cX 
                self.zy,self.zx = 2.0*self.zx*self.zy + self.cY, tmp 
                i -= 1
  
            self.color =( (i << 21) , (i << 10) , i*8)
            self.color = (i * 50 % 255, i * 90 % 255, i % 255)
            self.bitmap[self.x, self.y] = self.color
            self.texture = arcade.Texture('background', self.off_screen_image)
            self.background_sprite.texture = self.texture
            self.x = self.x + 1

            if self.x >= SCREEN_WIDTH:
                self.y += 1
                self.x = 0

            

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