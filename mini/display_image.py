import sys
import os
import glob
import pygame
import countdown


counter = countdown.Countdown(count = 3)
files = glob.glob(sys.argv[1] + '/*.JPG')
pygame.display.init()
screen = pygame.display.set_mode( ( 800, 480 ), pygame.FULLSCREEN )
current_file = 0
num_files = len(files)
if num_files == 0:
    exit('No files in directory')

counter = countdown.Countdown(count = 3)
filename = files[current_file]
picture = pygame.image.load(filename)
picture = pygame.transform.scale(picture, (800, 480))
rect = picture.get_rect()
screen.blit ( picture, rect )
pygame.display.flip()

while True:
    if counter.is_finished():
        # pygame.quit()
        # exit("Countdown finished!")
        current_file = (current_file + 1) % num_files
        filename = files[current_file]
        picture = pygame.image.load(filename)
        picture = pygame.transform.scale(picture, (800, 480))
        rect = picture.get_rect()
        screen.blit ( picture, rect )
        pygame.display.flip()
        counter = countdown.Countdown(count = 3)
#


# input()
# pygame.quit()
