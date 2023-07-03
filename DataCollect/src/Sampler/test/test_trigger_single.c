#include <libbladeRF.h>
#include <unistd.h>
#include <stdio.h>
#include "common/bladedevice.h"

int main(){

	int status;

	/* open device */
	printf("Opening device...\n");

	struct bladerf *dev;
	status = bladerf_open(&dev, SLAVE_ID);
	if(status != 0){
		fprintf(stderr, "Failed to open device: %s\n", bladerf_strerror(status));
		return status;
	}

	/* init trigger */
	printf("Initializing trigger...\n");

	struct bladerf_trigger trigger;
	status = bladerf_trigger_init(dev, BLADERF_CHANNEL_RX(0), BLADERF_TRIGGER_J51_1, &trigger);
	if(status != 0){
		fprintf(stderr, "Failed to init trigger: %s\n", bladerf_strerror(status));
		bladerf_close(dev);
		return status;
	}

	trigger.role = BLADERF_TRIGGER_ROLE_MASTER;

	/* arm trigger */
	printf("Arming trigger...\n");

	status = bladerf_trigger_arm(dev, &trigger, true, 0, 0);
	if(status != 0){
		fprintf(stderr, "Failed to arm trigger: %s\n", bladerf_strerror(status));
		bladerf_close(dev);
		return status;
	}

	/* fire trigger */
	printf("Firing trigger...\n");

	status = bladerf_trigger_fire(dev, &trigger);
	if(status != 0){
		fprintf(stderr, "Failed to fire trigger: %s\n", bladerf_strerror(status));
		bladerf_trigger_arm(dev, &trigger, false, 0, 0);
		bladerf_close(dev);
		return status;
	}

	/* deinit trigger */
	printf("Disarming trigger...\n");

	status = bladerf_trigger_arm(dev, &trigger, false, 0, 0);
	if(status != 0){
		fprintf(stderr, "Failed to deinit trigger: %s\n", bladerf_strerror(status));
		bladerf_trigger_arm(dev, &trigger, false, 0, 0);
		bladerf_close(dev);
		return status;
	}

	/* close device */
	printf("Closing device...\n");
	bladerf_close(dev);

	printf("Complete!\n");
	return 0;
}
