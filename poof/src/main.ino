
#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include <TFT_eSPI.h>
#include <Button2.h>
#include "bmp.h"

#ifndef TFT_DISPOFF
#define TFT_DISPOFF 0x28
#endif

#ifndef TFT_SLPIN
#define TFT_SLPIN 0x10
#endif

#define BUTTON_PIN 26
#define BUTTON_2_PIN 35
#define LED_PIN 15
#define CAMERA_PIN 2
#define POOF_PIN 13

#define COUNTDOWN_DELAY 800
#define COUNTDOWN_COUNT 5
#define COUNTDOWN_INTERVAL_MS 1000        // rate at which 1 countdown tick occurs
#define POOF_DURATION_MS 300             // duration to keep poofer valve open
#define PHOTO_DELAY_MS 310               // Time to wait to take photo
#define SHUTTER_PRESS_DURATION_MS 100    // How long to press the shutter
#define LOCKOUT_DURATION_MS 5000          // Keep people from accidentally re-triggering

Button2 btn1(BUTTON_PIN);
Button2 btn2(BUTTON_2_PIN);

hw_timer_t *timer = NULL;

/**********************
 * Variable Setup
**********************/

// button
uint64_t sequence_start_ms = 0;

// countdown
int8_t count = 0;
int8_t current_count = 0;

// poofer valve
bool poofer_open = false;
uint64_t poofer_start_ms = 0;
uint64_t poofer_end_ms = 0;

// camera shutter
bool camera_shutter_open = false;
uint64_t camera_start_ms = 0;
uint64_t camera_end_ms = 0;

bool lockout = false;
uint64_t lockout_until_ms = 0;

uint64_t now_ms;


/******************************
 * TFT Display
 ******************************/

TFT_eSPI tft = TFT_eSPI(135, 240); // Invoke custom library
char display_string[18];

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

void setup_screen_for_text()
{
  tft.setTextSize(2);
  tft.setTextColor(TFT_WHITE);
  tft.setCursor(0, 0);
  tft.setTextDatum(MC_DATUM);
  tft.setTextSize(7);
}

/*************************
 * Photo Poof
**************************/

void set_offsets(uint64_t base_time)
{
  sequence_start_ms = base_time + COUNTDOWN_DELAY;
  poofer_start_ms = sequence_start_ms + (COUNTDOWN_INTERVAL_MS * COUNTDOWN_COUNT);
  poofer_end_ms = poofer_start_ms + POOF_DURATION_MS;

  camera_start_ms = poofer_start_ms + PHOTO_DELAY_MS;
  camera_end_ms = camera_start_ms + SHUTTER_PRESS_DURATION_MS;

  lockout_until_ms = camera_end_ms + LOCKOUT_DURATION_MS;
}

void setup()
{
  Serial.begin(115200);

  while (!Serial && millis() < 5000);

  delay(500);

  btn1.setPressedHandler([](Button2 &b)
                         {
                           Serial.println("Button pressed!");
                           if (!lockout)
                           {
                             lockout = true;
                             set_offsets(timerReadMilis(timer));
                           }
                         });

  btn2.setPressedHandler([](Button2 &b)
                         {
                           Serial.println("Button pressed!");
                           if (!lockout)
                           {
                             lockout = true;
                             set_offsets(timerReadMilis(timer));
                           } });

  // setup LED pin
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // setup camera pin
  pinMode(CAMERA_PIN, OUTPUT);
  digitalWrite(CAMERA_PIN, HIGH);

  //setup poofer pin
  pinMode(POOF_PIN, OUTPUT);
  digitalWrite(POOF_PIN, HIGH);

  screen_init();
  setup_screen_for_text();
  display_photopoof_logo();

  // setup timer
  timer = timerBegin(0, 80, true);
}

void button_loop()
{
  btn1.loop();
  btn2.loop();
}

void loop()
{
  button_loop();
  if (lockout)  // countdown + poof sequence running
  {
    now_ms = timerReadMilis(timer);

    if (camera_start_ms < now_ms && !camera_shutter_open && now_ms < camera_end_ms)
    {
      digitalWrite(CAMERA_PIN, LOW); // shutter open
      camera_shutter_open = true;
    }

    if (poofer_start_ms < now_ms && !poofer_open && now_ms < poofer_end_ms)
    {
      digitalWrite(POOF_PIN, LOW); // poofer open
      poofer_open = true;
    }

    if (poofer_end_ms < now_ms && poofer_open)
    {
      digitalWrite(POOF_PIN, HIGH); // poofer close
      poofer_open = false;
    }

    if (camera_end_ms < now_ms && camera_shutter_open)
    {
      digitalWrite(CAMERA_PIN, HIGH); // shutter close
      camera_shutter_open = false;
    }

    current_count = 5 - ((now_ms - sequence_start_ms) / COUNTDOWN_INTERVAL_MS);
    if (count != current_count)
    {
      count = current_count;
      if (count >= 0 && count <= 5)
      {
        display_number(count);
      }
      else if (count >= -5) //waiting
      {
        display_text("Wait");
      }
    }

    if (lockout_until_ms < timerReadMilis(timer) && lockout)
    {
      timerRestart(timer);   // restart the timer just in case
      display_photopoof_logo();
      lockout = false;
    }
  }
}
