#include <libbladeRF.h>
#include <stdio.h>
#include <assert.h>
#include "bladedevice.h"
#include "clock.h"

#define ONBOARD_CLOCK (int)0
#define EXTERNAL_CLOCK (int)1

int test_clock_init(struct bladerf *master_dev, struct bladerf *slave_dev){

    /* check function output */
    if(clock_init(master_dev, slave_dev) != 0){
        fprintf(stderr, "[master, slave] Clock init failed\n");
        return -1;
    }
    
    /* check input selection (master) */
    bladerf_clock_select sel;
    bladerf_get_clock_select(master_dev, &sel);
    if(sel != ONBOARD_CLOCK){
        fprintf(stderr, "[master] Onboard clock not set\n");
        return -1;
    }

    /* check input selection (slave) */
    bladerf_get_clock_select(slave_dev, &sel);
    if(sel != EXTERNAL_CLOCK){
        fprintf(stderr, "[slave] External clock not set\n");
        return -1;
    }

    /* check output selection (master) */
    bool state;
    bladerf_get_clock_output(master_dev, &state);
    if(!state){
        fprintf(stderr, "[master] Clock output enable failed\n");
        return -1;
    }

    /* check output selection (slave) */
    bladerf_get_clock_output(slave_dev, &state);
    if(state){
        fprintf(stderr, "[slave] Clock output disable failed\n");
        return -1;
    }

    return 0;
}


int main(){

    int status;

    /* open devices */
    struct bladerf *dev1, *dev2;

    printf("[dev1] Opening device...\n");
    status = bladerf_open(&dev1, MASTER_ID);
    if(status != 0){
        printf("[dev1] Failed to open.\n");
        return -1;
    }

    printf("[dev2] Opening device...\n");
    status = bladerf_open(&dev2, SLAVE_ID);
    if(status != 0){
        bladerf_close(dev1);
        printf("[dev2] Failed to open.\n");
        return -1;
    }

    /* test clock_init() */

    printf("[dev1, dev2] Testing clock_init()...\n");
    if(test_clock_init(dev1, dev2) == -1){
        bladerf_close(dev1);
        bladerf_close(dev2);
        return -1;
    }

    /* close devices */

    printf("Complete. Closing devices\n");
    bladerf_close(dev1);
    bladerf_close(dev2);

    return 0;
}
