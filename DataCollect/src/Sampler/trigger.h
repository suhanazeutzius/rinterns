#ifndef _TRIGGER_H_
#define _TRIGGER_H_

#include <libbladeRF.h>
#include <stdio.h>

int trigger_init(struct bladerf *master_dev, struct bladerf *slave_dev, bladerf_trigger *master_trig, bladerf_trigger *slave_trig);
int trigger_deinit(struct bladerf *master_dev, struct bladerf *slave_dev, bladerf_trigger *master_trig, bladerf_trigger *slave_trig);
int trigger_fire(struct bladerf *master_dev, bladerf_trigger *master_trig);

#endif
