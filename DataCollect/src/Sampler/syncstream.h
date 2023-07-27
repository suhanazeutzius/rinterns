/**
 * @file syncstream.h
 * @author Nate Golding
 * @date Jul 2023
 * @brief Configuration of stream from bladeRF's to computer
 */

#ifndef _SYNCSTREAM_H_
#define _SYNCSTREAM_H_

#include <libbladeRF.h>
#include <stdio.h>
#include <string.h>
#include "common/buffers.h"
#include "channel.h"

struct stream_config{
    unsigned int num_samples;       /**<total number of samples to get */
    unsigned int num_buffers;       /**< number of buffers used on device-end */
    unsigned int buffer_size;       /**< number of samples per buffer on device-end */
    unsigned int num_transfers;     /**< number of device-end buffers "in-flight" on USB transfer at a time */
    unsigned int timeout_ms;        /**< timeout of each buffer transfer in ms */
};

struct syncstream_task_arg{
    struct stream_config st_config;
    struct bladerf *master_dev;
    struct bladerf *slave_dev;
    int status;                     /**< return status */
};

static int16_t *master_buffer = NULL;           /**< buffer to contain all samples from a collect */
static unsigned int master_buffer_len = 0;      /**< number of samples read into the buffer */
static int16_t *slave_buffer = NULL;            /**< buffer to contain all samples from a collect */
static unsigned int slave_buffer_len = 0;       /**< number of samples read into the buffer */

int syncstream_init(struct bladerf *master_dev, struct bladerf *slave_dev, struct stream_config st_config);
void *syncstream_init_task(void *arg);
int syncstream_handle_csv(struct bladerf *master_dev, struct bladerf *slave_dev, char *filename);
int syncstream_handle_buffers(struct bladerf *master_dev, struct bladerf *slave_dev, struct buffers *buffers);
void syncstream_free_buffers(void);

int _syncstream_init_config(struct bladerf *master_dev, struct bladerf *slave_dev, struct stream_config st_config);
int _syncstream_init_buffers(struct stream_config st_config);

#endif
