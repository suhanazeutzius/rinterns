#include "pll.h"


/**
 * Print the current PLL state information
 *
 * @param struct bladerf *dev -- device to get info from
 * @return returns 0 on success, bladerf error on failure
 *
 * @brief
 **/
int pll_state(struct bladerf *dev){

    int status;

    /* get enable */

    bool enabled;
    status = bladerf_get_pll_enable(dev, &enabled);
    if(status != 0){
        fprintf(stderr, "Failed to get pll enabled state: %s\n", bladerf_strerror(status));
    }
    else{
        printf("Enabled:\t%s\n", enabled ? "True" : "False");
    }

    /* get lock state */

    bool locked;
    status = bladerf_get_pll_lock_state(dev, &locked);
    if(status != 0){
        fprintf(stderr, "Failed to get pll lock state: %s\n", bladerf_strerror(status));
    }
    else{
        printf("Locked:\t%s\n", locked ? "True" : "False");
    }

    /* get ref clock frequency */

    uint64_t freq;
    status = bladerf_get_pll_refclk(dev, &freq);
    if(status != 0){
        fprintf(stderr, "Failed to get pll ref clock frequency: %s\n", bladerf_strerror(status));
    }
    else{
        printf("Frequency: %luHz\n", freq);
    }

    /* get registers */

    uint32_t val;
    status = bladerf_get_pll_register(dev, PLL_14BIT_REF_COUNTER_LATCH, &val);
    if(status != 0){
        fprintf(stderr, "Failed to get 14-bit Reference Counter: %s\n", bladerf_strerror(status));
    }
    else{
        // TODO
    }

    status = bladerf_get_pll_register(dev, PLL_13BIT_N_COUNTER_LATCH, &val);
    if(status != 0){
        fprintf(stderr, "Failed to get 13-bit N Counter: %s\n", bladerf_strerror(status));
    }
    else{
        // TODO
    }

    status = bladerf_get_pll_register(dev, PLL_FUNCTION_LATCH, &val);
    if(status != 0){
        fprintf(stderr, "Failed to get Function Latch: %s\n", bladerf_strerror(status));
    }
    else{
        // TODO
    }
    
    status = bladerf_get_pll_register(dev, PLL_INITIALIZATION_LATCH, &val);
    if(status != 0){
        fprintf(stderr, "Failed to get Initialization Latch: %s\n", bladerf_strerror(status));
    }
    else{
        // TODO
    }


    return 0;
}
