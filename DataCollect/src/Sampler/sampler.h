/**
 * @file sampler.h
 * @author Nate Golding
 * @date Jul 2023
 * @brief Sampling of 4 channel (2 blades, 2ch per blade)
 */

#ifndef _SAMPLER_H_
#define _SAMPLER_H_

#include <libbladeRF.h>
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include "clock.h"
#include "channel.h"
#include "trigger.h"
#include "syncstream.h"

int sampler(struct bladerf *master_dev, struct bladerf *slave_dev, struct channel_config ch_config, struct stream_config st_config);
int sampler_threaded(struct bladerf *master_dev, struct bladerf *slave_dev, struct channel_config ch_config, struct stream_config st_config);

int _sampler_init(struct bladerf *master_dev, struct bladerf *slave_dev, struct channel_config ch_config);

#endif
