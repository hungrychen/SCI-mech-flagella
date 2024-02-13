#include "Arduino.h"
#include "L298N_motorClass.h"

Motor::Motor(int in1, int in2, int en) {
  this->in1 = in1;
  this->in2 = in2;
  this->en = en;

  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(en, OUTPUT);

  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  this->dir = true;

  analogWrite(en, 0);
}

void Motor::setPWM(int newPWM){
  analogWrite(en, newPWM);
}

void Motor::run(int time){
  delay(time);
  analogWrite(en, 0);
}

void Motor::toggleDir(){
  digitalWrite(in1, dir);
  digitalWrite(in2, !dir);
  dir = !dir;
}

void Motor::setDir(bool newDir) {
  if(dir!=newDir) {
    dir = newDir;
    digitalWrite(in1, !dir);
    digitalWrite(in2, dir); 
  }
}