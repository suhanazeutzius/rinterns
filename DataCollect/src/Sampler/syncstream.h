#ifndef _SYNCSTREAM_H_
#define _SYNCSTREAM_H_

#include <libbladeRF.h>
#include <stdio.h>
#include "channel.h"

struct stream_config{
    unsigned int num_samples;
    unsigned int num_buffers;
    unsigned int buffer_size;
    unsigned int num_transfers;
    unsigned int timeout_ms;
};

static int16_t *master_buffer = NULL;
static int16_t *slave_buffer = NULL;

int syncstream_init(struct bladerf *master_dev, struct bladerf *slave_dev, struct stream_config st_config);
int syncstream_handle(struct bladerf *master_dev, struct bladerf *slave_dev);

#endif
