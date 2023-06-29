#ifndef _PHASEIMPOSER_H_
#define _PHASEIMPOSER_H_

#include <libbladeRF.h>
#include <stdio.h>
#include "phase.h"

int phaseimpose_buffers(int16_t **buf0, int16_t **buf1, int16_t **buf2, int16_t **buf3, struct delta_phase delta_phase);
int phaseimpose_csv(char *filename, struct delta_phase delta_phase);

#endif
