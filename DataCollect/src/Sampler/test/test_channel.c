#include <libbladeRF.h>
#include <stdio.h>
#include <assert.h>
#include "bladedevice.h"
#include "channel.h"


void test_channel_init(struct bladerf *dev, struct channel_config ch_config){

    /* check function return */

    assert(channel_init(dev, ch_config) == 0);

    /* gain mode */

    bladerf_gain_mode mode;
    bladerf_get_gain_mode(dev, BLADERF_CHANNEL_RX(0), &mode);
    assert(mode == ch_config.gainmode);
    
    bladerf_get_gain_mode(dev, BLADERF_CHANNEL_RX(1), &mode);
    assert(mode == ch_config.gainmode);

    /* gain value */

    if(ch_config.gainmode == BLADERF_GAIN_MGC){
        bladerf_gain gain;
        bladerf_get_gain(dev, BLADERF_CHANNEL_RX(0), &gain);
        assert(gain == ch_config.gain);
        
        bladerf_get_gain(dev, BLADERF_CHANNEL_RX(1), &gain);
        assert(gain == ch_config.gain);
    }

    /* sample rate */

    bladerf_sample_rate rate;
    bladerf_get_sample_rate(dev, BLADERF_CHANNEL_RX(0), &rate);
    assert(rate == ch_config.samplerate);

    bladerf_get_sample_rate(dev, BLADERF_CHANNEL_RX(1), &rate);
    assert(rate == ch_config.samplerate);

    /* bandwidth */

    bladerf_bandwidth bandwidth;
    bladerf_get_bandwidth(dev, BLADERF_CHANNEL_RX(0), &bandwidth);
    assert(bandwidth == ch_config.bandwidth);

    bladerf_get_bandwidth(dev, BLADERF_CHANNEL_RX(1), &bandwidth);
    assert(bandwidth == ch_config.bandwidth);

    /* frequency */

    bladerf_frequency frequency;
    bladerf_get_frequency(dev, BLADERF_CHANNEL_RX(0), &frequency);
    assert(frequency == ch_config.frequency);

    bladerf_get_frequency(dev, BLADERF_CHANNEL_RX(1), &frequency);
    assert(frequency == ch_config.frequency);

    return;
}





void test_channel_enable(struct bladerf *dev){

    /* check function return */
    assert(channel_enable(dev) == 0);
    return;
}





void test_channel_deinit(struct bladerf *dev){
    
    /* check function return */
    assert(channel_deinit(dev) == 0);
    return;
}





int main(){

    /* open devices */
     
    struct bladerf *dev1;
    struct bladerf *dev2;
    
    printf("[dev1] Opening device...\n");
    assert(bladerf_open(&dev1, DEVICE1_ID) == 0);

    printf("[dev2] Opening device...\n");
    assert(bladerf_open(&dev2, DEVICE2_ID) == 0);

    /* test channel_init() */

    struct channel_config ch_config;
    ch_config.gainmode = BLADERF_GAIN_SLOWATTACK_AGC;
    ch_config.gain = 0; 
    ch_config.samplerate = 30690000;
    ch_config.bandwidth = 18000000;
    ch_config.frequency = 1567420000;

    printf("[dev1] Testing channel_init()...\n");
    test_channel_init(dev1, ch_config);

    printf("[dev2] Testing channel_init()...\n");
    test_channel_init(dev2, ch_config);
    
    /* test channel_enable() */
    
    printf("[dev1] Testing channel_enable()...\n");
    test_channel_enable(dev1);

    printf("[dev2] Testing channel_enable()...\n");
    test_channel_enable(dev2);
    

    /* test channel_deinit() */

    printf("[dev1] Testing channel_deinit()...\n");
    test_channel_deinit(dev1);

    printf("[dev2] Testing channel_deinit()...\n");
    test_channel_deinit(dev2);


    /* close devices */

    printf("Complete. Closing devices.\n");
    bladerf_close(dev1);
    bladerf_close(dev2);

    return 0;
}
