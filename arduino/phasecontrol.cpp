#include "phasecontrol.h"

#include <Arduino.h>
#include "encoderconvs.h"

PhaseControl::PhaseControl() {
  // m_counts[0] = 0;
  // m_counts[1] = 0;
}

PhaseControl::~PhaseControl() {
}

void PhaseControl::initMotorPos() {
  m_counts[0] = 0;
  m_counts[1] = 0;

  // unsigned long leftover = m_counts[1] - m_counts[0];
  // leftover = abs(leftover);
  // if (m_counts[1] > m_counts[0]) {
  //   m_counts
  // }
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

void PhaseControl::getCorrectionTerm(double &termA, double &termB) const {
  double diffInRounds = getCoeff(1) - getCoeff(0);
  double activationRes = activation(diffInRounds);
  termA = activationRes;
  termB = -activationRes;
}

double PhaseControl::getCoeff(int motorIdx) const {
  if (motorIdx < 0 || motorIdx > 1) {
    Serial.println("ERROR: PhaseControl::getCoeff: invalid idx");
    exit(1);
  }
  double phase =  m_counts[motorIdx] / encoderToPhase;
  return phase;
}

double PhaseControl::activation(double coeff) const {
  if (coeff > CUTOFF)
    return CUTOFF;
  if (coeff < -CUTOFF)
    return -CUTOFF;
  return coeff;
}
