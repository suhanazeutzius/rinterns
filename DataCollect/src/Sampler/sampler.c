#include "sampler.h"

/**
 * initializes and takes a sample from two devices
 *
 * @param struct bladerf *master_dev -- master device (opened)
 * @param struct bladerf *slave_dev -- slave device (opened)
 * @param struct channel_config ch_config -- channel configuration parameters
 * @param struct stream_config st_config -- stream configuration parameters
 * @return int -- returns 0 on success, bladerf error code on failure
 *
 * @brief Devices should be opened prior to calling sampler, and ch_config and st_config should
 * be double checked for accuracy
 **/
int sampler(struct bladerf *master_dev, struct bladerf *slave_dev, struct channel_config ch_config, struct stream_config st_config){

	int status;

    /* init clock sharing */
    status = clock_init(master_dev, slave_dev);
    if(status != 0) return status;

    /* init channels */
    status = channel_init(master_dev, ch_config);
    if(status != 0) return status;

    status = channel_init(slave_dev, ch_config);
    if(status != 0) return status;

    /* init triggers */
    struct bladerf_trigger master_trig, slave_trig;
    status = trigger_init(master_dev, slave_dev, &master_trig, &slave_trig);
    if(status != 0) return status;

    /* init syncstream */
    status = syncstream_init(master_dev, slave_dev, st_config);
    if(status != 0) goto exit_fail;

    /* fire trigger */
    status = trigger_fire(master_dev, &master_trig);
    if(status != 0) goto exit_fail;

    /* handle syncstream */

    status = syncstream_handle_csv(master_dev, slave_dev, "sample.csv");
    if(status != 0) goto exit_fail;

    /* deinit triggers */

    trigger_deinit(master_dev, slave_dev, &master_trig, &slave_trig);

    /* disable modules */

    status = channel_disable(master_dev);
    if(status != 0){
        status = channel_disable(slave_dev);
        if(status != 0) return status;
        return status;
    }
    else{
        status = channel_disable(slave_dev);
        if(status != 0) return status;
    }

    /* return 0 on success */

	return 0;

exit_fail:
    trigger_deinit(master_dev, slave_dev, &master_trig, &slave_trig);
    return status;
}
