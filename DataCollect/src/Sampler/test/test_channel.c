#include <libbladeRF.h>
#include <stdio.h>
#include "common/bladedevice.h"
#include "channel.h"


int test_channel_init(struct bladerf *dev, struct channel_config ch_config){

    int status;

    /* check function return */

    status = channel_init(dev, ch_config);
    if(status != 0){
        fprintf(stderr, "Failed to initialize channels: %s\n", bladerf_strerror(status));
        return status;
    }

    /* gain mode ch0 */

    bladerf_gain_mode mode;
    status = bladerf_get_gain_mode(dev, BLADERF_CHANNEL_RX(0), &mode);
    
    if(status != 0){
        fprintf(stderr, "Failed to get gain mode on ch0: %s\n", bladerf_strerror(status));
        return status;
    }

    if(mode != ch_config.gainmode){
        fprintf(stderr, "Gainmode does not match config on ch0\n");
        return -1;
    }
    
    /* gain mode ch1 */

    status = bladerf_get_gain_mode(dev, BLADERF_CHANNEL_RX(1), &mode);
    
    if(status != 0){
        fprintf(stderr, "Failed to get gainmode on ch1: %s\n", bladerf_strerror(status));
        return status;
    }

    if(mode != ch_config.gainmode){
        fprintf(stderr, "Gainmode does not match config on ch1\n");
        return -1;
    }

    /* gain value */

    if(ch_config.gainmode == BLADERF_GAIN_MGC){
        bladerf_gain gain;
        status = bladerf_get_gain(dev, BLADERF_CHANNEL_RX(0), &gain);
        
        /* gain value ch0 */
 
        if(status != 0){
            fprintf(stderr, "Failed to get gain on ch0: %s\n", bladerf_strerror(status));
            return  status;
        }

        if(gain != ch_config.gain){
            fprintf(stderr, "Gain does not match config on ch0\n");
            return -1;
        }

        /* gain value ch1 */

        status = bladerf_get_gain(dev, BLADERF_CHANNEL_RX(1), &gain);
        
        if(status != 0){
            fprintf(stderr, "Failed to get gain on ch1: %s\n", bladerf_strerror(status));
            return status;
        }

        if(gain != ch_config.gain){
            fprintf(stderr, "Gain does not match config on ch1\n");
            return -1;
        }
    }

    /* sample rate ch0  */

    bladerf_sample_rate rate;
    status = bladerf_get_sample_rate(dev, BLADERF_CHANNEL_RX(0), &rate);

    if(status != 0){
        fprintf(stderr, "Failed to get samplerate on ch0: %s\n", bladerf_strerror(status));
        return status;
    }

    if(rate != ch_config.samplerate){
        fprintf(stderr, "Samplerate does not match config on ch0\n");
        return -1;
    }

    /* sample rate ch1  */

    status = bladerf_get_sample_rate(dev, BLADERF_CHANNEL_RX(1), &rate);

    if(status != 0){
        fprintf(stderr, "Failed to get samplerate on ch1: %s\n", bladerf_strerror(status));
        return status;
    }

    if(rate != ch_config.samplerate){
        fprintf(stderr, "Samplerate does not match config on ch1\n");
        return -1;
    }

    /* bandwidth ch0 */

    bladerf_bandwidth bandwidth;
    status = bladerf_get_bandwidth(dev, BLADERF_CHANNEL_RX(0), &bandwidth);

    if(status != 0){
        fprintf(stderr, "Failed to get bandwidth on ch0: %s\n", bladerf_strerror(status));
        return status;
    }

    if(bandwidth != ch_config.bandwidth){
        fprintf(stderr, "Bandwidth does not match config on ch0\n");
        return -1;
    }

    /* bandwidth ch1 */

    status = bladerf_get_bandwidth(dev, BLADERF_CHANNEL_RX(1), &bandwidth);

    if(status != 0){
        fprintf(stderr, "Failed to get bandwidth on ch1: %s\n", bladerf_strerror(status));
        return status;
    }

    if(bandwidth != ch_config.bandwidth){
        fprintf(stderr, "Bandwidth does not match config on ch1\n");
        return -1;
    }

    /* frequency ch0 */

    bladerf_frequency frequency;
    status = bladerf_get_frequency(dev, BLADERF_CHANNEL_RX(0), &frequency);

    if(status != 0){
        fprintf(stderr, "Failed to get frequency on ch0: %s\n", bladerf_strerror(status));
        return status;
    }

    if(frequency != ch_config.frequency){
        fprintf(stderr, "Frequency does not match config on ch0\n");
        return -1;
    }

    /* frequency ch1 */

    status = bladerf_get_frequency(dev, BLADERF_CHANNEL_RX(1), &frequency);

    if(status != 0){
        fprintf(stderr, "Failed to get frequency on ch1: %s\n", bladerf_strerror(status));
        return status;
    }

    if(frequency != ch_config.frequency){
        fprintf(stderr, "Frequency does not match config on ch1\n");
        return -1;
    }

    /* biastee ch0 */
    
    bool biastee;
    status = bladerf_get_bias_tee(dev, BLADERF_CHANNEL_RX(0), &biastee);

    if(status != 0){
        fprintf(stderr, "Failed to get biastee on ch0: %s\n", bladerf_strerror(status));
        return status;
    }

    if(biastee ^ ch_config.biastee){
        fprintf(stderr, "Biastee does not match config on ch0\n");
        return -1;
    }

    /* biastee ch1 */
    
    status = bladerf_get_bias_tee(dev, BLADERF_CHANNEL_RX(1), &biastee);

    if(status != 0){
        fprintf(stderr, "Failed to get biastee on ch1: %s\n", bladerf_strerror(status));
        return status;
    }

    if(biastee ^ ch_config.biastee){
        fprintf(stderr, "Biastee does not match config on ch1\n");
        return -1;
    }
    
    return 0;
}





int test_channel_enable(struct bladerf *dev){

    /* check function return */

    int status = channel_enable(dev);

    if(status != 0){
        fprintf(stderr, "Failed to enable channels: %s\n", bladerf_strerror(status));
        return status;
    }
    return 0;
}





int test_channel_disable(struct bladerf *dev){
    
    /* check function return */

    int status = channel_disable(dev);

    if(status != 0){
        fprintf(stderr, "Failed to deinit channels: %s\n", bladerf_strerror(status));
        return status;
    }
    return 0;
}





int main(){

    int status;

    /* open devices */
     
    struct bladerf *dev1;
    struct bladerf *dev2;
    
    printf("[dev1] Opening device...\n");
    status = bladerf_open(&dev1, MASTER_ID);
    if(status != 0){
        fprintf(stderr, "[dev1] Failed to open device: %s\n", bladerf_strerror(status));
        return -1;
    }

    printf("[dev2] Opening device...\n");
    status = bladerf_open(&dev2, SLAVE_ID);
    if(status != 0){
        fprintf(stderr, "[dev2] Failed to open device: %s\n", bladerf_strerror(status));
        return -1;
    }

    /* test channel_init() */

    struct channel_config ch_config;
    ch_config.gainmode = BLADERF_GAIN_SLOWATTACK_AGC;
    ch_config.gain = 0; 
    ch_config.samplerate = 30690000;
    ch_config.bandwidth = 18000000;
    ch_config.frequency = 1567420000;
    ch_config.biastee = true;

    printf("[dev1] Testing channel_init()...\n");
    if(test_channel_init(dev1, ch_config) != 0){
        bladerf_close(dev1);
        bladerf_close(dev2);
        fprintf(stderr, "[dev1] Channel init failed\n");
        return -1;
    }

    printf("[dev2] Testing channel_init()...\n");
    if(test_channel_init(dev2, ch_config) != 0){
        bladerf_close(dev1);
        bladerf_close(dev2);
        fprintf(stderr, "[dev2] Channel init failed\n");
        return -1;
    }
    
    /* test channel_enable() */
    
    printf("[dev1] Testing channel_enable()...\n");
    if(test_channel_enable(dev1) != 0){
        bladerf_close(dev1);
        bladerf_close(dev2);
        fprintf(stderr, "[dev1] Channel enable failed\n");
        return -1;
    }

    printf("[dev2] Testing channel_enable()...\n");
    if(test_channel_enable(dev2) != 0){
        bladerf_close(dev1);
        bladerf_close(dev2);
        fprintf(stderr, "[dev2] Channel enable failed\n");
        return -1;
    }
    

    /* test channel_disable() */

    printf("[dev1] Testing channel_disable()...\n");
    if(test_channel_disable(dev1) != 0){
        bladerf_close(dev1);
        bladerf_close(dev2);
        fprintf(stderr, "[dev1] Channel enable failed\n");
        return -1;
    }

    printf("[dev2] Testing channel_disable()...\n");
    if(test_channel_disable(dev2) != 0){
        bladerf_close(dev1);
        bladerf_close(dev2);
        fprintf(stderr, "[dev2] Channel enable failed\n");
        return -1;
    }

    /* close devices */

    printf("Complete. Closing devices.\n");
    bladerf_close(dev1);
    bladerf_close(dev2);

    return 0;
}
