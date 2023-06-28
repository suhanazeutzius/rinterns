#ifndef _CHANNEL_H_
#define _CHANNEL_H_

#include <libbladeRF.h>
#include <stdio.h>

struct channel_config{
    bladerf_gain_mode gainmode;
    bladerf_gain gain;
    bladerf_sample_rate samplerate;
    bladerf_bandwidth bandwidth;
    bladerf_frequency frequency;
    bool biastee;
};

int channel_init(struct bladerf *dev, struct channel_config ch_config);
int channel_enable(struct bladerf *dev);
int channel_disable(struct bladerf *dev);

#endif
