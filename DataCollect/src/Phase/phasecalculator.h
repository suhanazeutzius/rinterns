#ifndef _PHASECALC_H_
#define _PHASECALC_H_

#include <libbladeRF.h>
#include <stdio.h>
#include "phase.h"

int phasecalculator_buffers(struct buffers *buffers, struct delta_phase *delta_phase);
int phasecalculator_csv(char *filename, struct delta_phase *delta_phase);

#endif
