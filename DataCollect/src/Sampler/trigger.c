#include "trigger.h"


/**
 * Initialize and arm triggers
 *
 * @param struct bladerf *master_dev -- master device
 * @param struct balderf *slave_dev -- slave device
 * @param struct bladerf_trigger *master_trig -- trigger associated with master device
 * @param struct bladerf_trigger *slave_trig -- trigger associated with slave device
 * @return int -- return 0 on success, bladerf error code on failure
 *
 * @brief initializes AND arms triggers. This should be called AFTER initializing clock, channels, and
 * enabling modules, and called BEFORE initializing streams and recieving streams. 
 * Note that triggers should be disabled before disabling modules or else unwanted triggers may occur
 **/
int trigger_init(struct bladerf *master_dev, struct bladerf *slave_dev, struct bladerf_trigger *master_trig, struct bladerf_trigger *slave_trig){

	int status;

    bladerf_channel channel = BLADERF_CHANNEL_RX(0);
    bladerf_trigger_signal signal = BLADERF_TRIGGER_MINI_EXP_1;

	/* init master trigger */
	status = bladerf_trigger_init(master_dev, channel, signal, master_trig);
	if(status != 0){
		fprintf(stderr, "Failed to initialize master trigger: %s\n", bladerf_strerror(status));
		return status;
	}
	master_trig->role = BLADERF_TRIGGER_ROLE_MASTER;

	/* init slave trigger */
	bladerf_trigger_init(slave_dev, channel, signal, slave_trig);
	if(status != 0){
		fprintf(stderr, "Failed to initialie slave trigger: %s\n", bladerf_strerror(status));
		return status;
	}
	slave_trig->role = BLADERF_TRIGGER_ROLE_SLAVE;

	/* arm triggers */
	status = bladerf_trigger_arm(master_dev, master_trig, true, 0, 0);
	if(status != 0){
		fprintf(stderr, "Failed to arm master trigger: %s\n", bladerf_strerror(status));
		return status;
	}
	
	status = bladerf_trigger_arm(slave_dev, slave_trig, true, 0, 0);
	if(status != 0){
		bladerf_trigger_arm(master_dev, master_trig, false, 0, 0);
		fprintf(stderr, "Failed to arm slave trigger: %s\n", bladerf_strerror(status));
		return status;
	}

	return 0;
}




/**
 * de-initialize triggers
 *
 * @param struct bladerf *master_dev -- master device
 * @param struct bladerf *slave_dev -- slave devic
 * @param struct bladerf_trigger *master_trig -- master trigger
 * @param balderf_trigger *slave_trigger -- slave trigger
 * @return int -- return 0 on success, return bladerf error code on failure
 *
 * @brief disarms master and slave triggers 
 * Note: should be called PRIOR to disabling modules
 **/
int trigger_deinit(struct bladerf *master_dev, struct bladerf *slave_dev, struct bladerf_trigger *master_trig, struct bladerf_trigger *slave_trig){

	int status;

	/* disarm master trigger */
	status = bladerf_trigger_arm(master_dev, master_trig, false, 0, 0);
	if(status != 0){
		fprintf(stderr, "Failed to disarm master trigger: %s\n", bladerf_strerror(status));
		return status;
	}

	/* disarm slave trigger */
	status = bladerf_trigger_arm(slave_dev, slave_trig, false, 0, 0);
	if(status != 0){
		fprintf(stderr, "Failed to disarm slave trigger: %s\n", bladerf_strerror(status));
		return status;
	}

    /* set disabled role */
    master_trig->role = BLADERF_TRIGGER_ROLE_DISABLED;
    slave_trig->role = BLADERF_TRIGGER_ROLE_DISABLED;

	return 0;
}





/**
 * fire master trigger signal
 *
 * @param struct bladerf *master_dev -- master device
 * @param struct bladerf_trigger *master_trig -- master trigger
 * @return int -- return 0 on success, bladerf error code on failure
 *
 * @brief should be called after sync stream initialization (call sync_config()
 * and sync_rx()) and should be promptly followed by a stream handler
 * Note: timeout of stream should be greater than the latency between stream initialization
 * and this function call
 **/
int trigger_fire(struct bladerf *master_dev, struct bladerf_trigger *master_trig){

	int status;

	status = bladerf_trigger_fire(master_dev, master_trig);
	if(status != 0){
		fprintf(stderr, "Failed to fire master trigger: %s\n", bladerf_strerror(status));
		return status;
	}

	return 0;
}





/**
 * task for firing trigger
 *
 * @param void *arg -- will be interpreted as pointer to trigger_task_arg struct
 * @return NULL on failure, trigger pointer on success
 *
 * @brief unpacks void *arg into device and trigger, fires trigger
 **/ 
void *trigger_fire_task(void *arg){

    if(!arg) return NULL;

    /* unpack arguments */
    struct bladerf *dev = ((struct trigger_task_arg*)arg)->dev;
    struct bladerf_trigger *trig = ((struct trigger_task_arg*)arg)->trig;

    int status;

    status = bladerf_trigger_fire(dev, trig);
    if(status != 0){
        fprintf(stderr, "Failed to fire master trigger: %s\n", bladerf_strerror(status));
        return NULL;    // TODO add return values
    }

    return NULL;        // TODO add return values
}
