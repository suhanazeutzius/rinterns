#include <libbladeRF.h>
#include <stdio.h>
#include "syncstream.h"
#include "bladedevice.h"
#include "channel.h"


int main(){

    int status;

    /* open devices */
    struct bladerf *dev1, *dev2;

    printf("[dev1] Opening device...\n");
    status = bladerf_open(&dev1, MASTER_ID);
    if(status != 0){
        fprintf(stderr, "Failed to open device1: %s\n", bladerf_strerror(status));
        return -1;
    }

    printf("[dev2] Opening device...\n");
    status = bladerf_open(&dev2, SLAVE_ID);
    if(status != 0){
        bladerf_close(dev1);
        fprintf(stderr, "Failed to open device2: %s\n", bladerf_strerror(status));
        return -1;
    }

    /* init channels */
    struct channel_config ch_config;
    ch_config.gainmode = BLADERF_GAIN_SLOWATTACK_AGC;
    ch_config.gain = 0;
    ch_config.samplerate = 30690000;
    ch_config.bandwidth = 18000000;
    ch_config.frequency = 1567420000;

    printf("[dev1] Initializing channels\n");
    if(channel_init(dev1, ch_config)) goto exit_fail;

    printf("[dev2] Initializing channels\n");
    if(channel_init(dev2, ch_config)) goto exit_fail;

    printf("[dev1] Enabling channels\n");
    if(channel_enable(dev1)) goto exit_fail;

    printf("[dev2] Enabling channels\n");
    if(channel_enable(dev2)) goto exit_fail;

    /* configure streams */

    struct stream_config st_config;
    st_config.num_samples = 307200;
    st_config.num_buffers = 16;
    st_config.buffer_size = 2048;
    st_config.num_transfers = 8;
    st_config.timeout_ms = 3500;

    printf("[dev1] Initializing syncstream...\n");
    if(syncstream_init(dev1, dev2, st_config)) goto exit_fail;

    printf("[dev2] Initializing syncstream...\n");
    if(syncstream_handle(dev1, dev2)) goto exit_fail;

    /* deinit channels */

    printf("[dev1] Deinitializing channels...\n");
    if(channel_deinit(dev1)) goto exit_fail;

    printf("[dev2] Deinitializing channels...\n");
    if(channel_deinit(dev2)) goto exit_fail;


    printf("[dev1, dev2] Complete.\n");
    return 0;


exit_fail:
    bladerf_close(dev1);
    bladerf_close(dev2);
    return -1;
}
