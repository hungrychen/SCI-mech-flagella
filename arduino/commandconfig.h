#ifndef COMMANDCONFIG_H
#define COMMANDCONFIG_H

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
const char *       SYNC_SPEED_COMMAND        = "s";
const char *       SYNC_OPP_COMMAND          = "o";
const char *       UPDATE_COMMAND            = "update";
const char *       TARE_COMMAND              = "tare";
const int          MAX_COMMAND_WORDS         = 5;

#endif // COMMANDCONFIG_H