
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

#define SEGMENT_CLOCK_PIN 25
#define SEGMENT_DATA_PIN  27
#define SEGMENT_LATCH_PIN 33

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

#define SLOW_BLINK_DURATION 400
#define FAST_BLINK_DURATION 150

Button2 btn1(BUTTON_PIN);
Button2 btn2(BUTTON_2_PIN);

portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;
hw_timer_t *timer = NULL;
hw_timer_t *blink_timer = NULL;

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

bool led_status = false;
volatile bool led_change = false;

uint64_t now_ms;

//     -  A
//    / / F/B
//    -  G
//   / / E/C
//   -. D/DP

#define a 1 << 0
#define b 1 << 6
#define c 1 << 5
#define d 1 << 4
#define e 1 << 3
#define f 1 << 1
#define g 1 << 2
#define dp 1 << 7

/**************************
 * 7-Segment Display
**************************/
// Given a number, or '-', shifts it out to the display
void postNumber(byte number, boolean decimal)
{

  byte segments;

  switch (number)
  {
    case 1:
      segments = b | c;
      break;
    case 2:
      segments = a | b | d | e | g;
      break;
    case 3:
      segments = a | b | c | d | g;
      break;
    case 4:
      segments = f | g | b | c;
      break;
    case 5:
      segments = a | f | g | c | d;
      break;
    case 6:
      segments = a | f | g | e | c | d;
      break;
    case 7:
      segments = a | b | c;
      break;
    case 8:
      segments = a | b | c | d | e | f | g;
      break;
    case 9:
      segments = a | b | c | d | f | g;
      break;
    case 0:
      segments = a | b | c | d | e | f;
      break;
    case 'o':
      segments = c | d | e | g;    // small circle (low)
      break;
    case 'O':
      segments = a | b | f | g;    // small circle (high)
      break;
    case ' ':
      segments = 0;
      break;
    case 'c':
      segments = g | e | d;
      break;
    case '-':
      segments = g;
      break;
  }

  if (decimal) segments |= dp;

  // Clock these bits out to the drivers
  for (byte x = 0; x < 8; x++)
  {
    portENTER_CRITICAL_ISR(&timerMux);
    digitalWrite(SEGMENT_CLOCK_PIN, LOW);
    digitalWrite(SEGMENT_DATA_PIN, segments & 1 << (7 - x));
    portEXIT_CRITICAL_ISR(&timerMux);
    delayMicroseconds(150);
    portENTER_CRITICAL_ISR(&timerMux);
    digitalWrite(SEGMENT_CLOCK_PIN, HIGH); // Data transfers to the register on the rising edge of SRCK
    portEXIT_CRITICAL_ISR(&timerMux);
  }
}

void IRAM_ATTR flip_led() {
  portENTER_CRITICAL_ISR(&timerMux);
  digitalWrite(LED_PIN, !digitalRead(LED_PIN));
  led_change = true;
  portEXIT_CRITICAL_ISR(&timerMux);
}

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
  postNumber(num, false);
  portENTER_CRITICAL_ISR(&timerMux);
  digitalWrite(SEGMENT_LATCH_PIN, LOW);
  delayMicroseconds(50);
  digitalWrite(SEGMENT_LATCH_PIN, HIGH);
  portEXIT_CRITICAL_ISR(&timerMux);
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
  timerAlarmWrite(blink_timer, (1000 * SLOW_BLINK_DURATION), true);
  timerAlarmEnable(blink_timer);
}

void setup()
{
  Serial.begin(115200);

  while (!Serial && millis() < 5000);

  delay(500);

  btn1.setPressedHandler([](Button2 &button)
                         {
                           Serial.println("Button pressed!");
                           if (!lockout)
                           {
                             lockout = true;
                             set_offsets(timerReadMilis(timer));
                           }
                         });

  btn2.setPressedHandler([](Button2 &button)
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

  //setup LED arrow
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);

  //setup 7-segment display
  pinMode(SEGMENT_CLOCK_PIN, OUTPUT);
  pinMode(SEGMENT_DATA_PIN, OUTPUT);
  pinMode(SEGMENT_LATCH_PIN, OUTPUT);
  digitalWrite(SEGMENT_CLOCK_PIN, LOW);
  digitalWrite(SEGMENT_DATA_PIN, LOW);
  digitalWrite(SEGMENT_LATCH_PIN, LOW);

  screen_init();
  setup_screen_for_text();
  display_photopoof_logo();

  // setup timer
  timer = timerBegin(0, 80, true);
  blink_timer = timerBegin(1, 80, true);

  timerAttachInterrupt(blink_timer, &flip_led, true);
}

void loop()
{
  btn1.loop();  // check buttons
  btn2.loop();

  if (lockout)  // countdown + poof sequence are running
  {
    now_ms = timerReadMilis(timer);

    if (led_change)
    {
      // display_text("blink!");
      led_change = false;
    }

    if (camera_start_ms < now_ms && !camera_shutter_open && now_ms < camera_end_ms)
    {
      digitalWrite(CAMERA_PIN, LOW); // shutter open
      camera_shutter_open = true;
      camera_end_ms = camera_start_ms + SHUTTER_PRESS_DURATION_MS;
    }

    if (camera_end_ms < now_ms && camera_shutter_open)
    {
      digitalWrite(CAMERA_PIN, HIGH); // shutter close
      camera_shutter_open = false;
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

    current_count = 5 - ((now_ms - sequence_start_ms) / COUNTDOWN_INTERVAL_MS);
    if (count != current_count)
    {
      count = current_count;
      if (count > 0 && count <= 5)
      {
        display_number(count);    // display count
        if (count == 2)
        {
          timerAlarmWrite(blink_timer, (1000 * FAST_BLINK_DURATION), true);
        }

      }
      else if (count == 0)
      {
        timerAlarmDisable(blink_timer);
        digitalWrite(LED_PIN, LOW);
        digitalWrite(SEGMENT_LATCH_PIN, LOW);  // clear 7-segment
        postNumber(' ', false);
        digitalWrite(SEGMENT_LATCH_PIN, HIGH);
      }
      else if (count >= -5) //wait...
      {
        display_text("Wait");
      }
    }

    if (lockout_until_ms < timerReadMilis(timer) && lockout)
    {
      timerRestart(timer);   // restart the timer just in case
      digitalWrite(LED_PIN, HIGH);
      display_photopoof_logo();
      lockout = false;
    }
  }
}
