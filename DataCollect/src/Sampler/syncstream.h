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
static unsigned int master_buffer_len = 0;
static int16_t *slave_buffer = NULL;
static unsigned int slave_buffer_len = 0;

int syncstream_init(struct bladerf *master_dev, struct bladerf *slave_dev, struct stream_config st_config);
int syncstream_handle_csv(struct bladerf *master_dev, struct bladerf *slave_dev, char *filename);
int syncstream_handle_buffers(struct bladerf *master_dev, struct bladerf *slave_dev, int16_t **buf0,     int16_t **buf1, int16_t **buf2, int16_t **buf3);
void syncstream_free_buffers(void);

#endif
