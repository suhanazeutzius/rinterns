#ifndef _SAMPLER_H_
#define _SAMPLER_H_

#include <libbladeRF.h>
#include <stdio.h>
#include "clock.h"
#include "channel.h"
#include "trigger.h"
#include "syncstream.h"

int sampler(struct bladerf *master_dev, struct bladerf *slave_dev, struct channel_config ch_config, struct stream_config st_config);

#endif