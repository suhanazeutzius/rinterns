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
 */
int clock_init(struct bladerf *master_dev, struct bladerf *slave_dev){
	int status;

    /* set onboard reference for master */

    status = bladerf_set_clock_select(master_dev, CLOCK_SELECT_ONBOARD);
    if(status != 0){
        fprintf(stderr, "Failed to set onboard reference on master: %s\n", bladerf_strerror(status));
        return status;
    }

    /* set master clock output */

    status = bladerf_set_clock_output(master_dev, true);
    if(status != 0){
        fprintf(stderr, "Failed to enable output clock on master: %s\n", bladerf_strerror(status));
        return status;
    }

    /* set offboard reference for slave */

    status = bladerf_set_clock_select(slave_dev, CLOCK_SELECT_EXTERNAL);
    if(status != 0){
        fprintf(stderr, "Failed to set offboard reference on slave: %s\n", bladerf_strerror(status));
        return status;
    }

    /* disable slave clock output */

    status = bladerf_set_clock_output(slave_dev, false);
    if(status != 0){
        fprintf(stderr, "Failed to disable output clock on slave: %s\n", bladerf_strerror(status));
        return status;
    }

	return 0;
}





/**
 * Get vctcxo trim state
 *
 * @param struct bladerf *dev -- device to check
 * @return 0 on success, bladerf error on failure
 *
 * @brief
 */
int clock_vctcxo_state(struct bladerf *dev){

    int status;

    /* get calibration trim */

    uint16_t trim;
    status = bladerf_get_vctcxo_trim(dev, &trim);
    if(status != 0){
        fprintf(stderr, "Failed to get calibration trim: %s\n", bladerf_strerror(status));
    }
    else{
        printf("Calibration Trim:\t%u\n", trim);
    }

    /* get actual trim */

    status = bladerf_trim_dac_read(dev, &trim);
    if(status != 0){
        fprintf(stderr, "Failed to get actual trim: %s\n", bladerf_strerror(status));
    }
    else{
        printf("Actual Trim:\t\t%u\n", trim);
    }

    /* get tamer mode */

    int mode;
    status = bladerf_get_vctcxo_tamer_mode(dev, &mode);
    if(status != 0){
        fprintf(stderr, "Failed to get tamer mode: %s\n", bladerf_strerror(status));
    }
    else{
        switch(mode){
            case BLADERF_VCTCXO_TAMER_DISABLED:{
                printf("Tamer Disabled\n");
                break;
            }
            case BLADERF_VCTCXO_TAMER_1_PPS:{
                printf("1PPS Tamer Source\n");
                break;
            }
            case BLADERF_VCTCXO_TAMER_10_MHZ:{
                printf("10MHz Tamer Source\n");
                break;
            }
            default:{
                printf("Invalid Tamer Mode\n");
                break;
            }
        }
    }

    return 0;
}
