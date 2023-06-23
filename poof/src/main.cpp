#include <Arduino.h>

#include <TFT_eSPI.h>
#include <SPI.h>
#include <Wire.h>
#include <Button2.h>
#include "esp_adc_cal.h"
#include "bmp.h"

#ifndef TFT_DISPOFF
#define TFT_DISPOFF 0x28
#endif

#ifndef TFT_SLPIN
#define TFT_SLPIN 0x10
#endif

#define ADC_EN 14
#define ADC_PIN 34
#define BUTTON_1 35
#define BUTTON_2 0

#define COUNTDOWN_SPEED 1000

TFT_eSPI tft = TFT_eSPI(135, 240); // Invoke custom library
Button2 btn1(BUTTON_1);
Button2 btn2(BUTTON_2);

char buff[512];
int vref = 1100;

hw_timer_t *countdown_timer = NULL;
int count = -1;
int previous_count = -1;
bool countdown_in_progress = false;
char display_string[18];


void IRAM_ATTR countdown_ISR()
{
    if (count >= 0)
    {
        count--;
    }
}

void setup_timer(hw_timer_t *timer, void (*timer_callback)(void), int time_in_ms)
{
    timerAttachInterrupt(timer, timer_callback, false);
    timerAlarmWrite(timer, (1000 * time_in_ms), true);
    timerAlarmEnable(timer);
}

void button_init()
{
    btn1.setLongClickHandler([](Button2 &b)
    {
        int r = digitalRead(TFT_BL);
        tft.fillScreen(TFT_BLACK);
        tft.setTextColor(TFT_GREEN, TFT_BLACK);
        tft.setTextDatum(MC_DATUM);
        tft.drawString("Press again to wake up", tft.width() / 2, tft.height() / 2);
        digitalWrite(TFT_BL, !r);
    });
    btn1.setPressedHandler([](Button2 &b)
    {
        Serial.println("btn1 pressed!");
        if (!countdown_in_progress)
        {
            count = 6;
            countdown_in_progress = true;
            timerStart(countdown_timer);
        }
    });

    btn2.setPressedHandler([](Button2 &b)
    {
        Serial.println("btn2 pressed!");
    });
}

void button_loop()
{
    btn1.loop();
    btn2.loop();
}

void screen_init()
{
    tft.init();
    tft.setRotation(1);
    if (TFT_BL > 0)
    {                                           // TFT_BL has been set in the TFT_eSPI library in the User Setup file TTGO_T_Display.h
        pinMode(TFT_BL, OUTPUT);                // Set backlight pin to output mode
        digitalWrite(TFT_BL, TFT_BACKLIGHT_ON); // Turn backlight on. TFT_BACKLIGHT_ON has been set in the TFT_eSPI library in the User Setup file TTGO_T_Display.h
    }
    tft.setSwapBytes(true);
}

void setup_screen_for_text()
{
    tft.setTextSize(2);
    tft.setTextColor(TFT_WHITE);
    tft.setCursor(0, 0);
    tft.setTextDatum(MC_DATUM);
    tft.setTextSize(8);
}

void display_photopoof_logo()
{
    tft.pushImage(0, 0, 240, 135, photopoof_logo);
}

void setup()
{
    Serial.begin(115200);
    Serial.println("Welcome to Photo Poof!");

    countdown_timer = timerBegin(0, 80, true);
    setup_timer(countdown_timer, &countdown_ISR, COUNTDOWN_SPEED);
    screen_init();
    setup_screen_for_text();
    button_init();
}

void display_text(char *text)
{
    tft.fillScreen(TFT_BLACK);
    tft.drawString(text, tft.width() / 2, tft.height() / 2);
    Serial.println(text);
}

void display_number(int num)
{
    sprintf(display_string, "%d", num);
    display_text(display_string);
}

void loop()
{
    button_loop();
    if (count != previous_count)
    {
        previous_count = count;
        if (count > 5)
        {
            // noop
        }
        else if (count > 0)
        {
            display_number(count);
        }
        else if (count == 0)
        {
            display_text("Poof!");
        }
        else
        {
            display_photopoof_logo();
            countdown_in_progress = false;
            Serial.println("Ready...");
        }
    }
}
