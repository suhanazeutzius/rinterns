#include <libbladeRF.h>
#include <stdio.h>
#include "bladedevice.h"
#include "trigger.h"
#include "syncstream.h"


int test_trigger_init(struct bladerf *master_dev, struct bladerf *slave_dev, struct bladerf_trigger *master_trig, struct bladerf_trigger *slave_trig){

    int status;

    /* check function output */

    status = trigger_init(master_dev, slave_dev, master_trig, slave_trig);
    if(status != 0){
        fprintf(stderr, "[master, slave] Trigger init failed: %s\n", bladerf_strerror(status));
        return status;
    }

    /* check trigger state (master) */

    bool is_armed, has_fired, fire_requested;
    status = bladerf_trigger_state(master_dev, master_trig, &is_armed, &has_fired, &fire_requested, NULL, NULL);

    if(status != 0){
        fprintf(stderr, "[master] Failed to get trigger state: %s\n", bladerf_strerror(status));
        return status;
    }

    if(!is_armed){
        fprintf(stderr, "[master] Failed to arm trigger\n");
        return -1;
    }

    if(has_fired){
        fprintf(stderr, "[master] Device pre-emptively already fired\n");
        return -1;
    }

    if(fire_requested){
        fprintf(stderr, "[master] Device pre-emptively requested a fire\n");
        return -1;
    }

    /* check trigger state (slave) */

    status = bladerf_trigger_state(slave_dev, slave_trig, &is_armed, &has_fired, &fire_requested, NULL, NULL);

    if(status != 0){
        fprintf(stderr, "[slave] Failed to get trigger state: %s\n", bladerf_strerror(status));
        return status;
    }

    if(!is_armed){
        fprintf(stderr, "[slave] Failed to arm trigger\n");
        return -1;
    }

    if(has_fired){
        fprintf(stderr, "[slave] Device pre-emptively already fired\n");
        return -1;
    }

    if(fire_requested){
        fprintf(stderr, "[slave] Device pre-emptively requested a fire\n");
        return -1;
    }

    /* return 0 on success */
    
    return 0;
}





int test_trigger_fire(struct bladerf *master_dev, struct bladerf_trigger *master_trig){

    int status;

    /* check function return */

    status = trigger_fire(master_dev, master_trig);
    if(status != 0){
        fprintf(stderr, "[master] Trigger fire failed: %s\n", bladerf_strerror(status));
        return status;
    }

    /* check trigger state */

    bool is_armed, has_fired, fire_requested;
    status = bladerf_trigger_state(master_dev, master_trig, &is_armed, &has_fired, &fire_requested, NULL, NULL);

    if(status != 0){
        fprintf(stderr, "[master] Failed to get trigger state: %s\n", bladerf_strerror(status));
        return status;
    }

    if(!(has_fired || fire_requested)){
        fprintf(stderr, "[master] Trigger failed to enter has_fired or fire_requested state\n");
        return -1;
    }

    /* return 0 on success */

    return 0;
}





int test_trigger_deinit(struct bladerf *master_dev, struct bladerf *slave_dev, struct bladerf_trigger *master_trig, struct bladerf_trigger *slave_trig){
    
    int status;

    /* check function return */

    status = trigger_deinit(master_dev, slave_dev, master_trig, slave_trig);
    if(status != 0){
       fprintf(stderr, "[master, slave] Failed to deinit triggers: %s\n", bladerf_strerror(status));
        return status;
    }

    /* check trigger state (master) */

    bool is_armed, has_fired, fire_requested;
    status = bladerf_trigger_state(master_dev, master_trig, &is_armed, &has_fired, &fire_requested, NULL, NULL);
    if(status != 0){
        fprintf(stderr, "[master] Failed to get trigger state: %s\n", bladerf_strerror(status));
        return status;
    }

    if(is_armed){
        fprintf(stderr, "[master] Failed to disarm trigger\n");
        return -1;
    }

    /* check trigger state (slave) */
 
    status = bladerf_trigger_state(slave_dev, slave_trig, &is_armed, &has_fired, &fire_requested, NULL, NULL);
    if(status != 0){
        fprintf(stderr, "[slave] Failed to get trigger state: %s\n", bladerf_strerror(status));
        return status;
    }

    if(is_armed){
        fprintf(stderr, "[slave] Failed to disarm trigger\n");
        return -1;
    }

    /* return 0 on success */

    return 0;
}





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


    /* test trigger_init() */

    printf("[master, slave] Initializing triggers\n");

    struct bladerf_trigger master_trig, slave_trig;

    if(test_trigger_init(master_dev, slave_dev, &master_trig, &slave_trig) != 0){
        fprintf(stderr, "[master, slave] Failed to initialize triggers\n");
        bladerf_close(master_dev);
        bladerf_close(slave_dev);
        return -1;
    }

    /* test trigger_fire() */        
    
    printf("[master] Firing trigger...\n");
    if(test_trigger_fire(master_dev, &master_trig) != 0){
        fprintf(stderr, "[master] Failed to fire trigger\n");
        bladerf_close(master_dev);
        bladerf_close(slave_dev);
        return -1;
    }

    /* test trigger_deinit() */

    printf("[master, slave] Deinitializing triggers...\n");
    if(test_trigger_deinit(master_dev, slave_dev, &master_trig, &slave_trig) != 0){
        fprintf(stderr, "[master, slave] Failed to deinit triggers\n");
        bladerf_close(master_dev);
        bladerf_close(slave_dev);
        return -1;
    }

    /* return 0 on success */

    printf("[master, slave] Complete.\n");
    return 0;
}
