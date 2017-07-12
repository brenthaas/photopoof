import sys
import pygame

pygame.display.init()
screen = pygame.display.set_mode( ( 800, 480 ), pygame.FULLSCREEN )
picture = pygame.image.load ( sys.argv [ 1 ] )
picture = pygame.transform.scale(picture, (800, 480))
rect = picture.get_rect()
screen.blit ( picture, rect )
pygame.display.flip()
input()
pygame.quit()

