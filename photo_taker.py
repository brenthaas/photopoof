import countdown
import os
import pygame
import picamera
import sys
import time
from PIL import Image, ImageDraw, ImageFont

class PhotoTaker(object):
    """Manages camera and photo countdowns"""

    def render_font(self, text):
        font_size = 300 if len(text) > 2 else 800
        font = pygame.font.Font(None, font_size)
        return font.render(text, 1, (255,0,0))

    def clear_background(self):
        self.background = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA, 32)
        self.background.convert_alpha()
        self.background = self.background.convert()
        # self.background.fill(pygame.Color("white")) # fill with white

    def text_position(self, display_text):
        pos = display_text.get_rect()
        pos.centerx = self.background.get_rect().centerx
        pos.centery = self.background.get_rect().centery
        return pos

    def display_text(self, text):
        txt = self.render_font(text)
        self.clear_background()
        self.background.blit(txt, self.text_position(txt))
        self.screen.blit(self.background, (0,0))
        pygame.display.flip()

    def start_preview(self):
        self.countdown = countdown.Countdown(
            wait_message= "Ready?",
            final_message="POOF!"
        )
        self.camera.start_preview()

    def update_display(self, at_time=None):
        if at_time == None: at_time = time.time()
        if self.last_count != self.countdown.get_count():
            self.last_count = self.countdown.get_count()
            self.display_text(self.last_count)

    def is_done(self):
        return self.countdown.is_finished()

    def shutdown(self):
        pygame.quit()
        self.camera.stop_preview()

    def __init__(self, camera, image_path= "./images"):
        self.image_path = image_path
        self.camera = camera
        self.overlay_renderer = None
        self.last_count = None

        self.camera.preview_alpha = 200
        # Make the destination path for the photos
        if not os.path.exists(image_path):
            os.mkdir(image_path)

        # Display surface
        pygame.init()
        pygame.mouse.set_visible(0)
        w = pygame.display.Info().current_w
        h = pygame.display.Info().current_h
        screenSize = (w, h)
        self.font = ImageFont.truetype(
                        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
                        50)
        # Full screen the display with no window
        self.screen = pygame.display.set_mode(screenSize, pygame.FULLSCREEN)
        self.clear_background


if __name__ == "__main__":
    with picamera.PiCamera() as camera:
        camera.rotation = 270

        taker = PhotoTaker(camera)
        started = False

        while True:
            if not started:
                started = True
                taker.start_preview()
            taker.update_display()
            if taker.is_done():
                taker.shutdown()
                camera.close()
                sys.exit()
