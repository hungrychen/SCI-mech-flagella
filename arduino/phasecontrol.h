#ifndef PHASECONTROL_H
#define PHASECONTROL_H

class PhaseControl {
public:
  PhaseControl();
  ~PhaseControl();
  void initMotorPos();
  void encoderPhaseEventA();
  void encoderPhaseEventB();
  unsigned long getCounts(int motorIdx) const;
  void getCorrectionTerm(double &termA, double &termB) const;

private:
  static const double CUTOFF = 2.0;
  static const int NUM_MOTORS = 2;

  volatile unsigned long m_counts[NUM_MOTORS];

  double getCoeff(int motorIdx) const;
  double activation(double coeff) const;
};

#endif // PHASECONTROL_H