#include "clock.h"

/**
 * Initialize clock sharing
 *
 * @param struct bladerf *master_dev -- master device
 * @param struct bladerf *slave_dev -- slave device
 * @return int -- return 0 on success, bladerf error code on failure
 *
 * @brief initialize clock reference and clock sharing between master/slave
 * and initialize 10MHz reference
 **/
int clock_init(struct bladerf *master_dev, struct bladerf *slave_dev){
	int status;

    /* set onboard reference for master */

    status = bladerf_set_clock_select(master_dev, CLOCK_SELECT_ONBOARD);
    if(status != 0){
        fprintf(stderr, "Failed to set onboard reference on master: %s\n", bladerf_strerror(status));
        return status;
    }

    /* set offboard reference for slave */

    status = bladerf_set_clock_select(slave_dev, CLOCK_SELECT_EXTERNAL);
    if(status != 0){
        fprintf(stderr, "Failed to set offboard reference on slave: %s\n", bladerf_strerror(status));
        return status;
    }

    /* unset slave clock output */
    status = bladerf_set_clock_output(master_dev, false);
    if(status != 0){
        fprintf(stderr, "Failed to disable output clock on slave: %s\n", bladerf_strerror(status));
        return status;
    }

    /* set master clock output */

    status = bladerf_set_clock_output(slave_dev, true);
    if(status != 0){
        fprintf(stderr, "Failed to enable output clock on master: %s\n", bladerf_strerror(status));
        return status;
    }

	return 0;
}
