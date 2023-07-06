#include <libbladeRF.h>
#include <stdio.h>
#include <unistd.h>
#include "common/bladedevice.h"
#include "trigger.h"
#include "syncstream.h"


int main(){

    int status;

    /* open devices */

    struct bladerf *master_dev, *slave_dev;

    printf("[master] Opening device...\n");
    status = bladerf_open(&master_dev, MASTER_ID);
    if(status != 0){
        fprintf(stderr, "[master] Failed to open device: %s\n", bladerf_strerror(status));
        return -1;
    }

    printf("[slave] Opening device...\n");
    status = bladerf_open(&slave_dev, SLAVE_ID);
    if(status != 0){
        bladerf_close(master_dev);
        fprintf(stderr, "[slave] Failed to open device: %s\n", bladerf_strerror(status));
        return -1;
    }


    /* trigger_init() */

    printf("[master, slave] Initializing triggers\n");

    struct bladerf_trigger master_trig, slave_trig;

    if(trigger_init(master_dev, slave_dev, &master_trig, &slave_trig) != 0){
        fprintf(stderr, "[master, slave] Failed to initialize triggers\n");
        bladerf_close(master_dev);
        bladerf_close(slave_dev);
        return -1;
    }

    /* trigger_fire() */        
    
    printf("[master] Firing trigger...\n");
    if(trigger_fire(master_dev, &master_trig) != 0){
        fprintf(stderr, "[master] Failed to fire trigger\n");
        bladerf_close(master_dev);
        bladerf_close(slave_dev);
        return -1;
    }

    sleep(15);

    /* trigger_deinit() */

    printf("[master, slave] Deinitializing triggers...\n");
    if(trigger_deinit(master_dev, slave_dev, &master_trig, &slave_trig) != 0){
        fprintf(stderr, "[master, slave] Failed to deinit triggers\n");
        bladerf_close(master_dev);
        bladerf_close(slave_dev);
        return -1;
    }

    /* return 0 on success */

    printf("[master, slave] Complete.\n");
    return 0;
}
