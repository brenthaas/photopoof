import sys
import pygame

class ImageViewer(object):
    """Displays images"""

    def __init__(self):
        self.setup();

    def setup(self):
        pygame.display.init()
        self.screen = pygame.display.set_mode( ( 800, 480 ), pygame.FULLSCREEN )

    def display_image(self, filename):
        picture = pygame.image.load(filename)
        picture = pygame.transform.scale(picture, (800, 480))
        rect = picture.get_rect()
        self.screen.blit(picture, rect)
        pygame.display.flip()


if __name__ == "__main__":
    filename = sys.argv[1]
    viewer = ImageViewer()
    viewer.display_image(filename)
    input()
    pygame.quit()
    exit("Done")
