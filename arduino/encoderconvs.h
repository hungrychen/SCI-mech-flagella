#ifndef ENCODERCONVS_H
#define ENCODERCONVS_H

const float CPR = 12;
// const float gearRatio = 298.15;
const float gearRatio = 986.41;
const float encoderToPhase = CPR/4.*gearRatio;
const float encoderPMtoRPM = encoderToPhase/60.;

inline double encoderSpeedToRealSpeed(double d) {
  return d / encoderPMtoRPM;
}

inline double realSpeedToEncoderSpeed(double d) {
  return d * encoderPMtoRPM;
}

#endif