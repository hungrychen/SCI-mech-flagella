#ifndef PHASECONTROL_H
#define PHASECONTROL_H

class Motor;

class PhaseControl {
public:
  PhaseControl(Motor *motorA, Motor *motorB);
  ~PhaseControl();
  void initMotorPos();
  void encoderPhaseEventA();
  void encoderPhaseEventB();
  unsigned long getCounts(int motorIdx) const;
  void getCorrectionTerm(long &termA, long &termB) const;

private:
  Motor *m_motor[2];
  volatile unsigned long m_counts[2];

};

#endif // PHASECONTROL_H