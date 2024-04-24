// Speed measurement and control adapted from https://www.youtube.com/watch?v=HRaZLCBFVDE
#include <HX711_ADC.h>
#include <util/atomic.h>

#include "L298N_motorClass.h"
#include "pinconfig.h"
#include "commandconfig.h"
#include "phasecontrol.h"
#include "loadcellconfig.h"
#include "controlconfig.h"
#include "encoderconvs.h"

#define BAUD_RATE 2.5e5

#define A_DIR false
#define B_DIR false

// A_DIR: front motor direction
// B_DIR: rear motor direction
// false: counter-clockwise
// true:  clockwise

const unsigned long   MOTOR_UPDATE_INTERVAL   = 200;

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

PhaseControl phaseControl;

volatile unsigned long encoderCountsA;
volatile unsigned long encoderCountsB;

int targetSpeedA = 0;
int targetSpeedB = 0;

void encoderEventA() {
  encoderCountsA++;
  if (PHASE_CONTROL_ENABLE)
    phaseControl.encoderPhaseEventA();
}

void encoderEventB() {
  encoderCountsB++;
  if (PHASE_CONTROL_ENABLE)
    phaseControl.encoderPhaseEventB();
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
    F("time,LC1,LC1_filtered,LC2,LC2_filtered,encodedSpeedA,filteredSpeedA,encodedSpeedB,filteredSpeedB,phaseControlA,phaseControlB,"));
  delay(LC_STABILIZING_DELAY);

  if (PHASE_CONTROL_ENABLE)
    phaseControl.initMotorPos();

  attachInterrupt(digitalPinToInterrupt(encoderA2), encoderEventA, RISING);
  attachInterrupt(digitalPinToInterrupt(encoderB2), encoderEventB, RISING);
}

void loop() {
  static unsigned long prevSerialPrintTime = 0;
  static unsigned long prevMotorUpdateTime = 0;

  static bool motorStartedFlag     = false;
  static bool motorStopFlag        = false;
  static bool phaseControlEnFlag   = false;
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
    
    // Print time
    Serial.print(now/1000., 4);
    Serial.print(DATA_DELIMITER);
    Serial.print(i_1, 5);
    Serial.print(DATA_DELIMITER);  
    Serial.print(force_filter_1, 5);  
    Serial.print(DATA_DELIMITER);   
    Serial.print(i_2, 5);
    Serial.print(DATA_DELIMITER);    
    Serial.print(force_filter_2, 5);
    Serial.print(DATA_DELIMITER); 

    // Print speeds
    Serial.print(encoderSpeedToRealSpeed(measuredSpeedA));
    Serial.print(DATA_DELIMITER);
    Serial.print(encoderSpeedToRealSpeed(speed_filter_A));
    Serial.print(DATA_DELIMITER);
    Serial.print(encoderSpeedToRealSpeed(measuredSpeedB));
    Serial.print(DATA_DELIMITER);
    Serial.print(encoderSpeedToRealSpeed(speed_filter_B));
    Serial.print(DATA_DELIMITER);
    //   // Print constant 1
    // Serial.print(F("01"));

    // Serial.print(DATA_DELIMITER);
    Serial.print(pwmA);
    Serial.print(DATA_DELIMITER);
    Serial.print(pwmB);
    Serial.print(DATA_DELIMITER);

    // Print phases
    Serial.print(phaseControl.getCounts(0));
    Serial.print(DATA_DELIMITER);
    Serial.print(phaseControl.getCounts(1));
    // Serial.print(DATA_DELIMITER);

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
        speedAmount = realSpeedToEncoderSpeed(speedAmount);
        bool speedIsNegative = speedAmount < 0;
        speedAmount = abs(speedAmount);
        
        if (speedCommandType == SYNC_SPEED_COMMAND) {
          phaseControl.initMotorPos();
          phaseControlEnFlag = true;
        }
        else {
          phaseControlEnFlag = false;
        }

        if (speedCommandType == SET_SPEED_COMMAND || speedCommandType == SYNC_SPEED_COMMAND) {
          // switch (motorNum) {
          //   case 1:
          //     if (speedIsNegative)
          //       motorA.setDir(true);
          //     else
          //       motorA.setDir(false);
          //     targetSpeedA = speedAmount;
          //     if (!CONTROL_ENABLE) motorA.setPWM(speedAmount);
          //     break;
          //   case 2:
          //     if (speedIsNegative)
          //       motorB.setDir(true);
          //     else
          //       motorB.setDir(false);
          //     targetSpeedB = speedAmount;
          //     if (!CONTROL_ENABLE) motorB.setPWM(speedAmount);
          //     break;
          // }
          if (motorNum == 1 || speedCommandType == SYNC_SPEED_COMMAND) {
            if (speedIsNegative)
              motorA.setDir(true);
            else
              motorA.setDir(false);
            targetSpeedA = speedAmount;
            if (!CONTROL_ENABLE) motorA.setPWM(speedAmount);
          }
          if (motorNum == 2 || speedCommandType == SYNC_SPEED_COMMAND) {
            if (speedIsNegative)
              motorB.setDir(true);
            else
              motorB.setDir(false);
            targetSpeedB = speedAmount;
            if (!CONTROL_ENABLE) motorB.setPWM(speedAmount);
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

    double phaseTermA;
    double phaseTermB;

    if (!motorStartedFlag) {
      errIntA = errIntB = 0;
      motorStartedFlag = true;
    }
    if (phaseControlEnFlag) {
      phaseControl.getCorrectionTerm(phaseTermA, phaseTermB);
    }
    if (CONTROL_ENABLE) {
      controllerA = K_P*errA + K_I*errIntA + K_D*deA_dt;
      if (phaseControlEnFlag)
        controllerA += W_PHASE * phaseTermA;

      pwmA = controllerA;
      if      (pwmA > 255) pwmA = 255;
      else if (pwmA < 0)   pwmA = 0;
      motorA.setPWM(pwmA);
      controllerB = K_P*errB + K_I*errIntB + K_D*deB_dt;
      // Serial.print("controllerB, bef: ");
      // Serial.print(controllerB);
      if (phaseControlEnFlag)
        controllerB += W_PHASE * phaseTermB;
      // Serial.print("; phaseTermB: ");
      // Serial.print(phaseTermB);
      // Serial.print("; controllerB, aft: ");
      // Serial.println(controllerB);

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