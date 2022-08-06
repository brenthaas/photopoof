import machine, display, time, math, network, utime

class TFTDisplay:
    def __init__(self):
        self.tft = display.TFT()
        self.tft.init(self.tft.ST7789, bgr=False, rot=self.tft.LANDSCAPE,
                      miso=17, backl_pin=4, backl_on=1, mosi=19, clk=18,
                      cs=5, dc=16)
        self.tft.setwin(40,52,320,240)
        self.set_bg(0xFFFFFF) # Black on display
        self.set_fg(0x000000) # White
        self.top_margin = 10

    def demo(self):
        for i in range(0,241):
            color = 0xFFFFFF - self.tft.hsb2rgb(i/241*360, 1, 1)
            self.tft.line(i, 0, i, 135, color)

        self.tft.set_fg(0x000000)
        self.tft.ellipse(120, 67, 120, 67)
        self.tft.line(0, 0, 240, 135)

        text="ST7789 with micropython!"
        self.tft.text(120-int(self.tft.textWidth(text)/2),
                      67-int(self.tft.fontSize()[1]/2),
                      text,
                      0xFFFFFF)

    def get_line_offset(1):
        return self.top_margin + ((line - 1) * 20)

    def show_text(self, text, line=1):
        self.tft.text(0, get_line_offset(line), text)

    def clear_line(self, line):
        clear_text = " " * 100
        self.tft.text(0, get_line_offset(line), clear_text)

    def clear(self):
        self.tft.clear()