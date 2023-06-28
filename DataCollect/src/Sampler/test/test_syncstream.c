#include <libbladeRF.h>
#include <stdio.h>
#include <malloc.h>
#include "syncstream.h"
#include "bladedevice.h"
#include "channel.h"


int test_syncstream_handle_csv(struct bladerf *dev1, struct bladerf *dev2, struct stream_config st_config){

    printf("[dev1] Enabling channels\n");
    if(channel_enable(dev1)) return -1;

    printf("[dev2] Enabling channels\n");
    if(channel_enable(dev2)) return -1;

    /* configure streams */

    printf("[dev1, dev2] Initializing syncstream...\n");
    if(syncstream_init(dev1, dev2, st_config)) return -1;

    /* handle streams (csv) */

    printf("[dev1, dev2] Handling syncstream (csv)...\n");
    if(syncstream_handle_csv(dev1, dev2, "sample.csv")) return -1;

    /* deinit channels */

    printf("[dev1] Deinitializing channels...\n");
    if(channel_disable(dev1)) return -1;

    printf("[dev2] Deinitializing channels...\n");
    if(channel_disable(dev2)) return -1;

    /* return 0 on success */
    return 0;
}





int test_syncstream_handle_buffers(struct bladerf *dev1, struct bladerf *dev2, struct stream_config st_config){

    /* enable channels */

    printf("[dev1] Enabling channels\n");
    if(channel_enable(dev1)) return -1;

    printf("[dev2] Enabling channels\n");
    if(channel_enable(dev2)) return -1;
    
    /* configure streams */
 
    printf("[dev1, dev2] Initializing syncstream...\n");
    if(syncstream_init(dev1, dev2, st_config)) return -1;

    /* Handle streams (buffers) */

    printf("[dev1, dev2] Handling syncstream (buffers)...\n");
    int16_t *buf0, *buf1, *buf2, *buf3;
    if(syncstream_handle_buffers(dev1, dev2, &buf0, &buf1, &buf2, &buf3)) return -1;

    /* Check buffer sizes */
    printf("[dev1, dev2] Checking buffer sizes...\n");

    size_t buf_size;

    if(malloc_usable_size(buf0) < 2*st_config.num_samples){
        fprintf(stderr, "[dev1, dev2] Buffer 0 is undersized\n");
        goto exit_fail;
    }

    if(malloc_usable_size(buf1) < 2*st_config.num_samples){
        fprintf(stderr, "[dev1, dev2] Buffer 1 is undersized\n");
        goto exit_fail;
    }

    if(malloc_usable_size(buf2) < 2*st_config.num_samples){
        fprintf(stderr, "[dev1, dev2] Buffer 2 is undersized\n");
        goto exit_fail;
    }

    if(malloc_usable_size(buf3) < 2*st_config.num_samples){
        fprintf(stderr, "[dev1, dev2] Buffer 3 is undersized\n");
        goto exit_fail;
    }

    /* return 0 on success */
    return 0;

exit_fail:
    free(buf0);
    free(buf1);
    free(buf2);
    free(buf3);
    return -1;
}





int main(){

    int status;

    struct channel_config ch_config;
    ch_config.gainmode = BLADERF_GAIN_SLOWATTACK_AGC;
    ch_config.gain = 0;
    ch_config.samplerate = 30690000;
    ch_config.bandwidth = 18000000;
    ch_config.frequency = 905000000;
    ch_config.biastee = true;

    struct stream_config st_config;
    st_config.num_samples = 307200;
    st_config.num_buffers = 16;
    st_config.buffer_size = 2048;
    st_config.num_transfers = 8;
    st_config.timeout_ms = 10000;

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

    printf("[dev1] Initializing channels\n");
    if(channel_init(dev1, ch_config)) goto exit_fail;

    printf("[dev2] Initializing channels\n");
    if(channel_init(dev2, ch_config)) goto exit_fail;

    /* test handle csv */

    printf("[dev1, dev2] Testing handle csv...\n");
    if(test_syncstream_handle_csv(dev1, dev2, st_config)) goto exit_fail;

    /* test handle buffers */

    printf("[dev1, dev2] Test handle buffers...\n");
    if(test_syncstream_handle_buffers(dev1, dev2, st_config)) goto exit_fail;

    /* return 0 on success */

    printf("[dev1, dev2] Complete.\n");
    return 0;


exit_fail:
    bladerf_close(dev1);
    bladerf_close(dev2);
    return -1;
}
