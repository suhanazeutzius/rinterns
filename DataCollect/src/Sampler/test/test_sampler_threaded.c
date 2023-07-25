#include "sampler.h"
#include "common/bladedevice.h"

int main(){

    int status;

    /* setup configurations */

    struct channel_config ch_config;
    ch_config.gainmode = BLADERF_GAIN_SLOWATTACK_AGC;
    ch_config.gain = 0;
    ch_config.samplerate = 2048000;
    ch_config.frequency = 1575420000;
    ch_config.bandwidth = 18000000;
    ch_config.biastee = true;

    struct stream_config st_config;
    st_config.num_samples = 20480;
    st_config.num_buffers = 16;
    st_config.buffer_size = 2048;
    st_config.num_transfers = 8;
    st_config.timeout_ms = 20000;


    /* open devices */

    struct bladerf *dev1, *dev2;

    printf("[dev1] Opening device...\n");
    status = bladerf_open(&dev1, MASTER_ID);
    if(status != 0){
        fprintf(stderr, "[dev1] Failed to open device: %s\n", bladerf_strerror(status));
        return status;
    }

    printf("[dev2] Opening device...\n");
    status = bladerf_open(&dev2, SLAVE_ID);
    if(status != 0){
        bladerf_close(dev2);

        fprintf(stderr, "[dev2] Failed to open device: %s\n", bladerf_strerror(status));
        return status;
    }

    /* run sampler */

    printf("[dev1, dev2] Running sampler...\n");
    status = sampler_threaded(dev1, dev2, ch_config, st_config);
    if(status != 0){

        fprintf(stderr, "[dev1, dev2] Sampler failed: %s\n", bladerf_strerror(status));

        bladerf_close(dev1);
        bladerf_close(dev2);
        return status;
    }

    printf("Complete.\n");
    return 0;
}
