from machine import Pin, SoftI2C
import ssd1306

# Start I2C Communication SCL = 4 and SDA = 5 on Wemos Lolin32 ESP32 with built-in SSD1306 OLED
i2c = SoftI2C(scl=Pin(4), sda=Pin(5))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

class ScreenLogger:
    def __init__(self, row_names=['default']):
        self.names = row_names
        self.messages = dict()
        for name in row_names:
            intro = "Hello %s"%(name)
            self.messages[name] = "%-16s" % intro
        self.setup_screen()
        self.render_all()

    def setup_screen(self):
        i2c = SoftI2C(scl=Pin(4), sda=Pin(5))
        oled_width = 128
        oled_height = 64
        self.oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

    def add_row(self, name):
        self.names.append(name)
        self.messages[name] = 'Hello!'
        self.render_all()

    def render_all(self):
        self.oled.fill(0)
        for idx, name in enumerate(self.names):
            message = "%s: %s"%(name, self.messages.get(name))
            self.oled.text(message, 0, idx * 10)
        self.oled.show()

    def update(self, name, message):
        self.messages[name] = "%-16s" % message
        self.render_all()