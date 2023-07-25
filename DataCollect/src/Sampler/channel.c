#include "channel.h"


/**
 * initialize rx channels on a device
 *
 * @param struct bladerf *dev -- device to initialize
 * @param struct channel_config ch_config -- struct specifying channel parameters
 * @return int -- returns 0 on success, bladerf error code on failure
 *
 * @brief sets bandwidth, freq, gain, etc.
 */
int channel_init(struct bladerf *dev, struct channel_config ch_config){

    int status;

    /* set gain mode */

    status = bladerf_set_gain_mode(dev, BLADERF_CHANNEL_RX(0), ch_config.gainmode);
    if(status != 0){
        fprintf(stderr, "Failed to set gain mode on ch0: %s\n", bladerf_strerror(status));
        return status;
    }

    status = bladerf_set_gain_mode(dev, BLADERF_CHANNEL_RX(1), ch_config.gainmode);
    if(status != 0){
        fprintf(stderr, "Failed to set gain mode on ch1: %s\n", bladerf_strerror(status));
        return status;
    }


    /* set gain value (if manual gain mode selected) */

    if(ch_config.gainmode == BLADERF_GAIN_MGC){

        status = bladerf_set_gain(dev, BLADERF_CHANNEL_RX(0), ch_config.gain);
        if(status != 0){
            fprintf(stderr, "Failed to set gain on ch0: %s\n", bladerf_strerror(status));
            return status;
        }

        status = bladerf_set_gain(dev, BLADERF_CHANNEL_RX(1), ch_config.gain);
        if(status != 0){
            fprintf(stderr, "Failed to set gain on ch1: %s\n", bladerf_strerror(status));
            return status;
        }
    }

    /* set sample rate */

    status = bladerf_set_sample_rate(dev, BLADERF_CHANNEL_RX(0), ch_config.samplerate, NULL);
    if(status != 0){
        fprintf(stderr, "Failed to set samplerate on ch0: %s\n", bladerf_strerror(status));
        return status;
    }

    status = bladerf_set_sample_rate(dev, BLADERF_CHANNEL_RX(1), ch_config.samplerate, NULL);
    if(status != 0){
        fprintf(stderr, "Failed to set samplerate on ch1: %s\n", bladerf_strerror(status));
        return status;
    }

    /* set bandwidth */

    status = bladerf_set_bandwidth(dev, BLADERF_CHANNEL_RX(0), ch_config.bandwidth, NULL);
    if(status != 0){
        fprintf(stderr, "Failed to set bandwidth on ch0: %s\n", bladerf_strerror(status));
        return status;
    }
    
    status = bladerf_set_bandwidth(dev, BLADERF_CHANNEL_RX(1), ch_config.bandwidth, NULL);
    if(status != 0){
        fprintf(stderr, "Failed to set bandwidth on ch1: %s\n", bladerf_strerror(status));
        return status;
    }

    /* set frequency */

    status = bladerf_set_frequency(dev, BLADERF_CHANNEL_RX(0), ch_config.frequency);
    if(status != 0){
        fprintf(stderr, "Failed to set frequency on ch0: %s\n", bladerf_strerror(status));
        return status;
    }
    
    status = bladerf_set_frequency(dev, BLADERF_CHANNEL_RX(1), ch_config.frequency);
    if(status != 0){
        fprintf(stderr, "Failed to set frequency on ch1: %s\n", bladerf_strerror(status));
        return status;
    }

    /* set bias tee */

    status = bladerf_set_bias_tee(dev, BLADERF_CHANNEL_RX(0), ch_config.biastee);
    if(status != 0){
        fprintf(stderr, "Failed to set biastee on ch0: %s\n", bladerf_strerror(status));
        return status;
    }

    status = bladerf_set_bias_tee(dev, BLADERF_CHANNEL_RX(1), ch_config.biastee);
    if(status != 0){
        fprintf(stderr, "Failed to set biastee on ch1: %s\n", bladerf_strerror(status));
        return status;
    }


    return 0;

}





/**
 * enables rx channels on a device
 *
 * @param struct bladerf *dev -- device to enable channels on
 * @return int -- returns 0 on success, bladerf error code on failure
 *
 * @brief enables both modules; should be called after sync config
 */
int channel_enable(struct bladerf *dev){

    int status;

    /* enable ch 0 */

    status = bladerf_enable_module(dev, BLADERF_CHANNEL_RX(0), true);
    if(status != 0){
        fprintf(stderr, "Failed to enable ch0: %s\n", bladerf_strerror(status));
        return status;
    }

    /* enable ch 1 */

    status = bladerf_enable_module(dev, BLADERF_CHANNEL_RX(1), true);
    if(status != 0){
        fprintf(stderr, "Failed to enable ch1: %s\n", bladerf_strerror(status));
        return status;
    }

    return 0;
}





/**
 * deinitialize rx channels on a device
 *
 * @param struct bladerf *dev -- device to deinit
 * @return int -- returns 0 on success, bladerf error code on failure 
 *
 * @brief disables modules; does not mess with bandwidth, freq, etc.
 */
int channel_disable(struct bladerf *dev){

    int status;

    /* disable ch 0 */

    status = bladerf_enable_module(dev, BLADERF_CHANNEL_RX(0), false);
    if(status != 0){
        fprintf(stderr, "Failed to disable ch0: %s\n", bladerf_strerror(status));
        return status;
    }

    /* disable ch 1 */

    status = bladerf_enable_module(dev, BLADERF_CHANNEL_RX(1), false);
    if(status != 0){
        fprintf(stderr, "Failed to disable ch1: %s\n", bladerf_strerror(status));
        return status;
    }

    return 0;
}
