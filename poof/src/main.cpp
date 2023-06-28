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
#define BUTTON_1 0
#define BUTTON_2 35

#define BUTTON_PIN 26
#define LED_PIN 15
#define CAMERA_PIN 2
#define POOF_PIN 13

#define COUNTDOWN_SPEED 1000        // rate at which 1 countdown tick occurs
#define POOF_DURATION 300           // duration to keep poofer valve open
#define PHOTO_DELAY 400             // Time to wait to take photo
#define SHUTTER_PRESS_DURATION 150  // How long to press the shutter

portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

TFT_eSPI tft = TFT_eSPI(135, 240); // Invoke custom library
Button2 btn1(BUTTON_PIN);
Button2 btn2(BUTTON_2);

char buff[512];
int vref = 1100;

// Timers
hw_timer_t *countdown_timer = NULL;
hw_timer_t *poofer_timer = NULL;
hw_timer_t *camera_timer = NULL;
hw_timer_t *blink_timer = NULL;

// Countdown Variables
int count = -1;
int previous_count = -1;
bool poof_in_progress = false;
bool prev_poof_status = false;
bool lockout = false;
bool photo_in_progress = false;
bool photo_delayed = true;
bool open_shutter = false;


//////////////////////////////
// Display Info

char display_string[18];

void display_photopoof_logo()
{
  tft.pushImage(0, 0, 240, 135, photopoof_logo);
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

//////////////////////////////
// Timer Callbacks

void IRAM_ATTR countdown_ISR()
{
  portENTER_CRITICAL_ISR(&timerMux);
  --count;
  portEXIT_CRITICAL_ISR(&timerMux);
}

void IRAM_ATTR camera_ISR()
{
  portENTER_CRITICAL_ISR(&timerMux);
  if (photo_delayed)                // First Time Through
  {
    photo_delayed = false;
    digitalWrite(CAMERA_PIN, LOW);  // Open Shutter
    open_shutter = true;
  } else if (open_shutter)
  {
    digitalWrite(CAMERA_PIN, HIGH); // Close Shutter
    open_shutter = false;
    photo_in_progress = false;
  }
  portEXIT_CRITICAL_ISR(&timerMux);
}

void IRAM_ATTR poofer_done_ISR()
{
  portENTER_CRITICAL_ISR(&timerMux);
  digitalWrite(POOF_PIN, HIGH);
  poof_in_progress = false;
  portEXIT_CRITICAL_ISR(&timerMux);
}

//////////////////////////////
// Timer Helpers

void setup_timer(hw_timer_t *timer, void (*timer_callback)(void), int time_in_ms)
{
  timerAttachInterrupt(timer, timer_callback, false);
  timerAlarmWrite(timer, (1000 * time_in_ms), true);
  timerAlarmEnable(timer);
}

void breakdown_timer(hw_timer_t *timer)
{
  timerAlarmDisable(timer);
  timerDetachInterrupt(timer);
  timerStop(timer);
}

//////////////////////////////
// Action Start

void poofer_start()
{
  display_text("Poof!");
  poof_in_progress = true;
  setup_timer(poofer_timer, &poofer_done_ISR, POOF_DURATION);
  timerStart(poofer_timer);
  digitalWrite(POOF_PIN, LOW);
}

void camera_start()
{
  photo_delayed = true;
  photo_in_progress = true;
  setup_timer(camera_timer, &camera_ISR, PHOTO_DELAY);
  timerStart(camera_timer);
}

void countdown_start()
{
  lockout = true;
  count = 6;
  setup_timer(countdown_timer, &countdown_ISR, COUNTDOWN_SPEED);
  timerStart(countdown_timer);
}

//////////////////////////////
// Init GPIO things

void button_init()
{
  // btn1.setLongClickHandler([](Button2 &b)
  // {
  //     int r = digitalRead(TFT_BL);
  //     tft.fillScreen(TFT_BLACK);
  //     tft.setTextColor(TFT_GREEN, TFT_BLACK);
  //     tft.setTextDatum(MC_DATUM);
  //     tft.drawString("Press again to wake up", tft.width() / 2, tft.height() / 2);
  //     digitalWrite(TFT_BL, !r);
  // });
  btn1.setPressedHandler([](Button2 &b)
  {
    Serial.println("btn1 pressed!");
    if (!lockout)
    {
      countdown_start();
    }
  });

  btn2.setPressedHandler([](Button2 &b)
  {
    Serial.println("btn2 pressed!");
    if (!lockout)
    {
      countdown_start();
    }
  });
}

void pin_init()
{
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  pinMode(CAMERA_PIN, OUTPUT);
  digitalWrite(CAMERA_PIN, HIGH);

  pinMode(POOF_PIN, OUTPUT);
  digitalWrite(POOF_PIN, HIGH);
}

//////////////////////////////
// Screen Init

void screen_init()
{
  tft.init();
  tft.setRotation(1);
  if (TFT_BL > 0)
  {                                         // TFT_BL has been set in the TFT_eSPI library in the User Setup file TTGO_T_Display.h
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
  tft.setTextSize(7);
}

//////////////////////////////
// Setup

void setup()
{
  Serial.begin(115200);
  Serial.println("Welcome to Photo Poof!");

  // setup timers
  countdown_timer = timerBegin(0, 80, true);
  // setup_timer(countdown_timer, &countdown_ISR, COUNTDOWN_SPEED);
  poofer_timer = timerBegin(1, 80, true);
  // setup_timer(poofer_timer, &poofer_done_ISR, POOF_DURATION);
  camera_timer = timerBegin(2, 80, true);
  // setup_timer(camera_timer, &camera_ISR, PHOTO_DELAY);
  // setup_timer(unlock_timer, &lockout_done_ISR, LOCKOUT_DURATION);

  screen_init();
  setup_screen_for_text();
  display_photopoof_logo();
  pin_init();
  button_init();
}


//////////////////////////////
// Main Loop

void button_loop()
{
  btn1.loop();
  btn2.loop();
}

void loop()
{
  button_loop();
  if (count != previous_count)
  {
    previous_count = count;
    if (count > 5)
    {
      display_text("Go!");
    }
    else if (count > 0)
    {
      display_number(count);
    }
    else if (count == 0 && !poof_in_progress)
    {
      poofer_start();
      camera_start();
    }
    else if (count < -5)
    {
      lockout = false;
      // timerStop(countdown_timer);
      breakdown_timer(countdown_timer);
      breakdown_timer(poofer_timer);
      breakdown_timer(camera_timer);
      display_photopoof_logo();
    }
    else
    {
      sprintf(display_string, "%d...", 5+count);
      display_text(display_string);
    }
  }

  // Use different timing for shutter than for delay
  // if (!photo_delayed)
  // {
  //   if (open_shutter) // delay over
  //   {
  //     timerAlarmWrite(camera_timer, (1000 * SHUTTER_PRESS_DURATION), false);
  //     photo_delayed = true;
  //   } else // phhoto done
  //   {
  //     photo_delayed = true;
  //   }
  // }
}
