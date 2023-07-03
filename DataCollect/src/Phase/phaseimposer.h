#ifndef _PHASEIMPOSER_H_
#define _PHASEIMPOSER_H_

#include <libbladeRF.h>
#include <stdio.h>
#include <math.h>
#include <complex.h>
#include "phase.h"
#include "common/buffers.h"

int phaseimpose_buffers(struct buffers *buffers, struct delta_phase delta_phase);
int phaseimpose_csv(char *filename, struct delta_phase delta_phase);

#endif
