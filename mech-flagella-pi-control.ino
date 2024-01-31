// Speed measurement and control adapted from https://www.youtube.com/watch?v=HRaZLCBFVDE
#include "HX711_ADC.h"
#include "L298N_motorClass.h"
#include "util/atomic.h"

#define BAUD_RATE 2.5e5

#define enA 45
#define in1 41
#define in2 40

#define enB 44
#define in3 43
#define in4 42

#define encoderA1 21
#define encoderA2 20

#define encoderB1 19
#define encoderB2 18

// Swapped motors for debug
// #define enB 45
// #define in3 41
// #define in4 40

// #define enA 44
// #define in1 43
// #define in2 42

// #define encoderB1 21
// #define encoderB2 20

// #define encoderA1 19
// #define encoderA2 18

#define A_DIR false
#define B_DIR false

// A_DIR: front motor direction
// B_DIR: rear motor direction
// false: counter-clockwise
// true:  clockwise

const char         STOP_CHAR                 = 'x';
const char         COMMAND_DELIMITER         = ' ';
const char *       DIR_COMMAND               = "direction";
const int          DIR_COMMAND_MIN_WORDS     = 3;
const char *       LEFT_COMMAND              = "left";
const char *       RIGHT_COMMAND             = "right";
const char *       SPEED_COMMAND             = "speed";
const int          SPEED_COMMAND_MIN_WORDS   = 4;
const char *       ADD_SPEED_COMMAND         = "+";
const char *       SUBTRACT_SPEED_COMMAND    = "-";
const char *       SET_SPEED_COMMAND         = "=";
const char *       UPDATE_COMMAND            = "update";
const char *       TARE_COMMAND              = "tare";
const int          MAX_COMMAND_WORDS         = 5;
const unsigned long   MOTOR_UPDATE_INTERVAL   = 200;

  // ---LOAD CELL CONSTANTS---
const int HX711_dout_1  = 11; //mcu > HX711 dout pin
const int HX711_sck_1   = 10; //mcu > HX711 sck pin
const int HX711_dout_2  = 3; //mcu > HX711 dout pin
const int HX711_sck_2   = 2; //mcu > HX711 sck pin

const bool LC1_REVERSED = true;
const bool LC2_REVERSED = true;

const float CAL_VAL_1 = 13792.30;
const float CAL_VAL_2 = 13750.00;
// const long  TARE_OFFSET_1 = 8302430;
// const long  TARE_OFFSET_2 = 8304919;
const unsigned long LC_STABILIZING_DELAY = 5e3;

const unsigned long SERIAL_PRINT_INTERVAL = 10;
const char DATA_DELIMITER = ',';

  // filters
float force_filter_1 = 0.0;
float force_filter_2 = 0.0;
const float alpha = 0.072;
float speed_filter_A = 0.0;
float speed_filter_B = 0.0;
const float alpha_speed = 0.072;

  // HX711 constructor
HX711_ADC LoadCell_1(HX711_dout_1, HX711_sck_1);
HX711_ADC LoadCell_2(HX711_dout_2, HX711_sck_2);

Motor motorA(in1, in2, enA);
Motor motorB(in3, in4, enB);

volatile unsigned long encoderCountsA;
volatile unsigned long encoderCountsB;

int targetSpeedA = 0;
int targetSpeedB = 0;

bool CONTROL_ENABLE = 1;

const double K_P = 0.05; //0.05;
const double K_I = 0.08;
const double K_D = 0.0; //0.0;

void encoderEventA() {
  encoderCountsA++;
}

void encoderEventB() {
  encoderCountsB++;
}

void setup() {
  motorA.setDir(A_DIR);
  motorB.setDir(B_DIR);

  pinMode(encoderA1, INPUT);
  pinMode(encoderA2, INPUT);
  pinMode(encoderB1, INPUT);
  pinMode(encoderB2, INPUT);

  Serial.begin(BAUD_RATE);
  Serial.println();
  
  // Old speed input
    // Serial.print(F("Enter Speed A: "));
    // while (!Serial.available());
    // String targetSpeedA_str = Serial.readStringUntil('\n');
    // targetSpeedA = targetSpeedA_str.toInt();
    // Serial.print(F("Enter Speed B: "));
    // while (!Serial.available());
    // String targetSpeedB_str = Serial.readStringUntil('\n');
    // targetSpeedB = targetSpeedB_str.toInt();
  //

  LoadCell_1.begin();
  LoadCell_2.begin();
  if (LC1_REVERSED) {
    LoadCell_1.setReverseOutput();
    Serial.println(F("Set LC1 reversed"));
  }
  if (LC2_REVERSED) {
    LoadCell_2.setReverseOutput();
    Serial.println(F("Set LC2 reversed"));
  }

  unsigned long stabilizingtime = 5e3; // tare preciscion can be improved by adding a few seconds of stabilizing time
  const bool tare = true; //set this to false if you don't want tare to be performed in the next step
  LoadCell_1.start(stabilizingtime, tare);
  LoadCell_2.start(stabilizingtime, tare);
  delay(500);
  if (LoadCell_1.getTareTimeoutFlag() || LoadCell_2.getTareTimeoutFlag()) {
    Serial.println("Timeout, check MCU>HX711 wiring and pin designations");
    while (1);
  }

  LoadCell_1.setCalFactor(CAL_VAL_1); // set calibration factor (float)
  LoadCell_2.setCalFactor(CAL_VAL_2); // set calibration factor (float)

  while (!LoadCell_1.update() || !LoadCell_2.update());
  Serial.println("Startup is complete");
  Serial.println("LC1: CalFactor: " + String(LoadCell_1.getCalFactor())
    + " TareOffset: " + String(LoadCell_1.getTareOffset()) + String(LC1_REVERSED ? " Reversed" : ""));
  Serial.println("LC2: CalFactor: " + String(LoadCell_2.getCalFactor())
    + " TareOffset: " + String(LoadCell_2.getTareOffset()) + String(LC2_REVERSED ? " Reversed" : ""));

  Serial.println();
  Serial.println(
    F("LC1,LC1_filtered,LC2,LC2_filtered,encodedSpeedA,filteredSpeedA,encodedSpeedB,filteredSpeedB,time,DUMMY"));
  delay(LC_STABILIZING_DELAY);

  attachInterrupt(digitalPinToInterrupt(encoderA2), encoderEventA, RISING);
  attachInterrupt(digitalPinToInterrupt(encoderB2), encoderEventB, RISING);
}

/// @brief 
void loop() {
  static unsigned long prevSerialPrintTime = 0;
  static unsigned long prevMotorUpdateTime = 0;

  static bool motorStartedFlag     = false;
  static bool motorStopFlag        = false;
  static int  pwmA                 = 0;
  static int  pwmB                 = 0;
  static long prevSpeedSetTime     = 0;
  static long prevSpeedHandleTime  = 0;
  static long prevSpeedMeasureTime = 0;

  static long double prevErrA, errIntA = 0;
  static long double prevErrB, errIntB = 0;

  unsigned long currEncoderCountA;
  unsigned long currEncoderCountB;
  static double measuredSpeedA = 0.0;
  static double measuredSpeedB = 0.0;
  double controllerA, controllerB;
  long now = millis();

    // HANDLE SERIAL DATA PRINT
  if ((LoadCell_1.update() || LoadCell_2.update())
      && now > prevSerialPrintTime + SERIAL_PRINT_INTERVAL) {
    prevSerialPrintTime = now;

    float i_1 = LoadCell_1.getData();
    float i_2 = LoadCell_2.getData();
    
    force_filter_1 = (1-alpha)*force_filter_1 + alpha*i_1;
    force_filter_2 = (1-alpha)*force_filter_2 + alpha*i_2;
    
    Serial.print(i_1, 5);
    Serial.print(DATA_DELIMITER);  
    Serial.print(force_filter_1, 5);  
    Serial.print(DATA_DELIMITER);   
    Serial.print(i_2, 5);
    Serial.print(DATA_DELIMITER);    
    Serial.print(force_filter_2, 5);
    Serial.print(DATA_DELIMITER); 
      // Print time
    Serial.print(now/1000., 4);
    Serial.print(DATA_DELIMITER);
      // Print speeds
    Serial.print(measuredSpeedA/21*6);
    Serial.print(DATA_DELIMITER);
    Serial.print(speed_filter_A/21*6);
    Serial.print(DATA_DELIMITER);
    Serial.print(measuredSpeedB/21*6);
    Serial.print(DATA_DELIMITER);
    Serial.print(speed_filter_B/21*6);
    Serial.print(DATA_DELIMITER);
      // Print constant 1
    Serial.print(F("01"));

    Serial.print(DATA_DELIMITER);
    Serial.print(pwmA);
    Serial.print(DATA_DELIMITER);
    Serial.print(pwmB);

    Serial.println();
  }

    // SERIAL INPUT PROCESSOR
  if (now > prevMotorUpdateTime + MOTOR_UPDATE_INTERVAL) {
    prevMotorUpdateTime = now;
      // Get input from computer
    String inputText;
    while (Serial.available())
      inputText.concat(static_cast<char>(Serial.read()));
    inputText.toLowerCase();
    inputText.trim();

    if (inputText.length() > 0) {
        // Process input from computer
        // Stop code
      if (inputText.charAt(0) == STOP_CHAR) {
        motorA.setPWM(0);
        motorB.setPWM(0);
        while (1);
      }

      String parsedCommand[MAX_COMMAND_WORDS];
      int wordsParsed;
      unsigned start = 0;
      for (wordsParsed = 0; wordsParsed < MAX_COMMAND_WORDS; wordsParsed++) {
        int space = inputText.indexOf(COMMAND_DELIMITER, start);
        if (space == -1) break;
        parsedCommand[wordsParsed] = inputText.substring(start, space);
        start = space+1;
      }
      if (wordsParsed < MAX_COMMAND_WORDS)
        parsedCommand[wordsParsed] = inputText.substring(start);
      wordsParsed++;

      const String &commandInput = parsedCommand[0];
      unsigned motorNum = -1;
      if (commandInput == TARE_COMMAND) {
        motorA.setPWM(0);
        motorB.setPWM(0);

        delay(2000);
        Serial.print("Tare in 3, ");
        delay(1000);
        Serial.print("2, ");
        delay(1000);
        Serial.print("1, ");
        delay(1000);
        Serial.println("0");

        LoadCell_1.tareNoDelay();
        LoadCell_2.tareNoDelay();
        Serial.println("Tare complete");
        delay(1000);
        motorStartedFlag = false;
      }
      else if (commandInput == DIR_COMMAND || commandInput == SPEED_COMMAND
            || commandInput == UPDATE_COMMAND) {
        motorNum = parsedCommand[1].toInt();
      }
        // 1-30-24: edits were made to this section to enable negative speeds
      if (commandInput == SPEED_COMMAND && wordsParsed >= SPEED_COMMAND_MIN_WORDS) {
        const String &speedCommandType = parsedCommand[2];
        int speedAmount = parsedCommand[3].toInt();
        // Serial.println("speedAmount: " + String(speedAmount));
        bool speedIsNegative = speedAmount < 0;
        speedAmount = abs(speedAmount);

        if (speedCommandType == SET_SPEED_COMMAND) {
          switch (motorNum) {
            case 1:
              if (speedIsNegative)
                motorA.setDir(true);
              else
                motorA.setDir(false);
              targetSpeedA = speedAmount;
              if (!CONTROL_ENABLE) motorA.setPWM(speedAmount);
              break;
            case 2:
              if (speedIsNegative)
                motorB.setDir(true);
              else
                motorB.setDir(false);
              targetSpeedB = speedAmount;
              if (!CONTROL_ENABLE) motorB.setPWM(speedAmount);
              break;
          }
        }


      }
    }
  }

    // HANDLE MOTOR CONTROL
  // if (now > 20e3 && now-prevSpeedHandleTime > 10 && !motorStopFlag) {
  if (now-prevSpeedHandleTime > 10) {
    prevSpeedHandleTime = now;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
      currEncoderCountA = encoderCountsA;
      currEncoderCountB = encoderCountsB;
      encoderCountsA = encoderCountsB = 0;
    }
    long nowMicros = micros();
    double dt = ((nowMicros-prevSpeedMeasureTime) / 1.0e6);
    measuredSpeedA = (double) (currEncoderCountA) / dt;
    measuredSpeedB = (double) (currEncoderCountB) / dt;

    speed_filter_A = (1-alpha_speed)*speed_filter_A + alpha_speed*measuredSpeedA;
    speed_filter_B = (1-alpha_speed)*speed_filter_B + alpha_speed*measuredSpeedB;

    double errA = (targetSpeedA-speed_filter_A);
    errIntA += errA*dt;
    double deA_dt = (errA-prevErrA) / dt;
    double errB = (targetSpeedB-speed_filter_B);
    errIntB += errB*dt;
    double deB_dt = (errB-prevErrB) / dt;

    if (!motorStartedFlag) {
      errIntA = errIntB = 0;
      motorStartedFlag = true;
    }
    if (CONTROL_ENABLE) {
      controllerA = K_P*errA + K_I*errIntA + K_D*deA_dt;
      pwmA = controllerA;
      if      (pwmA > 255) pwmA = 255;
      else if (pwmA < 0)   pwmA = 0;
      motorA.setPWM(pwmA);
      controllerB = K_P*errB + K_I*errIntB + K_D*deB_dt;
      pwmB = controllerB;
      if      (pwmB > 255) pwmB = 255;
      else if (pwmB < 0)   pwmB = 0;
      motorB.setPWM(pwmB);
    }

    prevErrA = errA;
    prevErrB = errB;
    prevSpeedMeasureTime = nowMicros;
  }
}