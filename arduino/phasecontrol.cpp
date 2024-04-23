#include "phasecontrol.h"

#include <Arduino.h>
#include "L298N_motorClass.h"

PhaseControl::PhaseControl(Motor *motorA, Motor *motorB) {
  m_motor[0] = motorA;
  m_motor[1] = motorB;
}

PhaseControl::~PhaseControl() {
}

void PhaseControl::initMotorPos() {
  m_counts[0] = 0;
  m_counts[1] = 0;
}

void PhaseControl::encoderPhaseEventA() {
  m_counts[0]++;
}

void PhaseControl::encoderPhaseEventB() {
  m_counts[1]++;
}

unsigned long PhaseControl::getCounts(int motorIdx) const {
  if (motorIdx < 0 || motorIdx > 1) {
    Serial.println("ERROR: PhaseControl::getPhase: invalid idx");
    exit(1);
  }
  return m_counts[motorIdx];
}

void PhaseControl::getCorrectionTerm(long &termA, long &termB) const {
  long diff = abs(m_counts[0] - m_counts[1]);
  if (m_counts[0] < m_counts[1]) {
    termA = diff;
    termB = -diff;
  }
  else if (m_counts[0] > m_counts[1]) {
    termA = -diff;
    termB = diff;
  }
  else {
    termA = 0;
    termB = 0;
  }
}
