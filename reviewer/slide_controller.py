from live_slideshow import LiveSlideshow
import RPi.GPIO as GPIO

class SlideController:
    def __init__(self, dir, reset_button, display_duration=3500):
        """Gives users control over slideshow display"""
        GPIO.setmode(GPIO.BCM)
        self.reset_button = reset_button
        GPIO.setup(reset_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(reset_button, GPIO.FALLING, self.handle_button)
        self.slides = LiveSlideshow(dir, display_duration)

    def handle_button(self, another_option):
        self.slides.reset_slideshow()

if __name__ == '__main__':
    import sys

    try:
        path = sys.argv[1] if len(sys.argv) > 1 else "/home/pi/Desktop/photopoof"
        controller = SlideController(dir=path, reset_button=23)
    except Exception as ex:
        print("Closing due to exception" + ex)
