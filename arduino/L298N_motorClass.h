#ifndef L298N_motorClass_h
#define L298N_motorClass_h

#include "Arduino.h"

class Motor {
public:
  Motor(int in1, int in2, int en); // Constructor

  void setPWM(int newPWM);

  void run(int time); // runs irrespective of togglePwr, toggles off after

  void toggleDir();
  void setDir(bool newDir);

private:
  // Pinouts
  int in1, in2, en;

  // Useful Trackers
  bool dir;
};

#endif