#ifndef _CLOCK_H_
#define _CLOCK_H_

#include <libbladeRF.h>
#include <stdio.h>

int clock_init(struct bladerf *master_dev, struct bladerf *slave_dev);
int clock_vctcxo_state(struct bladerf *dev);

#endif
