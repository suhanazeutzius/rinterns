#include <libbladeRF.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "common/bladedevice.h"
#include "syncstream.h"
#include "channel.h"

int main(){

	int status;

    struct channel_config ch_config;
    ch_config.gainmode = BLADERF_GAIN_SLOWATTACK_AGC;
    ch_config.gain = 0;
    ch_config.samplerate = 30690000;
    ch_config.frequency = 1573420000;
    ch_config.bandwidth = 18000000;
    ch_config.biastee = true;

    struct stream_config st_config;
    st_config.num_samples = 61440;
    st_config.num_buffers = 16;
    st_config.buffer_size = 2048;
    st_config.num_transfers = 8;
    st_config.timeout_ms = 20000;

	/* open device */
	printf("Opening device...\n");

	struct bladerf *dev;
	status = bladerf_open(&dev, SLAVE_ID);
	if(status != 0){
		fprintf(stderr, "Failed to open device.\n");
		return -1;
	}

	/* init channels */
	printf("Initializing channels...\n");

	status = channel_init(dev, ch_config);
	if(status != 0){
		fprintf(stderr, "Failed to init channel.\n");
		bladerf_close(dev);
		return -1;
	}

	/* init trigger (slave) */
	printf("Initializing trigger...\n");

	struct bladerf_trigger trig;
	status = bladerf_trigger_init(dev, BLADERF_CHANNEL_RX(0), BLADERF_TRIGGER_J51_1, &trig);
	if(status != 0){
		fprintf(stderr, "Failed to init trigger.\n");
		bladerf_close(dev);
		return -1;
	}
	trig.role = BLADERF_TRIGGER_ROLE_SLAVE;

	/* arm trigger */
	printf("Arming trigger...\n");

	status = bladerf_trigger_arm(dev, &trig, true, 0, 0);
	if(status != 0){
		fprintf(stderr, "Failed to arm trigger.\n");
		bladerf_close(dev);
		trig.role = BLADERF_TRIGGER_ROLE_DISABLED;
		return -1; 
	}

	/* initialize syncstream */
	printf("Initializing syncstream...\n");

    status = bladerf_sync_config(dev, BLADERF_RX_X2, BLADERF_FORMAT_SC16_Q11, st_config.num_buffers, st_config.buffer_size, st_config.num_transfers, st_config.timeout_ms);
    if(status != 0){
        fprintf(stderr, "Failed to configure stream.\n");
        return -1;
    }

	/* allocate stream buffer */
	printf("Allocating buffer...\n");

    const unsigned int buf_size = st_config.num_samples * 2 * 2 * sizeof(int16_t);

    int16_t *buf = (int16_t*)malloc(buf_size);
    if(!buf){
        fprintf(stderr, "Failed to allocate buffer\n");
		bladerf_trigger_arm(dev, &trig, false, 0, 0);
		trig.role = BLADERF_TRIGGER_ROLE_DISABLED;
        bladerf_close(dev);
		return -1;
    }
	memset(buf, 0, buf_size);
    unsigned int buf_len = (unsigned int)(buf_size / sizeof(int16_t));

    /* enable RF front ends */
	printf("Enabling RF front end...\n");

    status = channel_enable(dev);
    if(status != 0){
		fprintf(stderr, "Failed to enable RF front end.\n");
		free(buf);
		bladerf_trigger_arm(dev, &trig, false, 0, 0);
		trig.role = BLADERF_TRIGGER_ROLE_DISABLED;
		bladerf_close(dev);
		return -1;
	}

    /* start stream recieve (master) */
	printf("Starting recieve stream...\n");

    status = bladerf_sync_rx(dev, buf, st_config.num_samples * 2, NULL, st_config.timeout_ms);
    if(status != 0){
        fprintf(stderr, "Failed to start sync rx stream (memory freed)\n");
		free(buf);
		bladerf_trigger_arm(dev, &trig, false, 0, 0);
		trig.role = BLADERF_TRIGGER_ROLE_DISABLED;
		bladerf_close(dev);
		return -1;	
    }

	/* wait for trigger */
	printf("Waiting for trigger...\n");

	/* check buffer */
	printf("Checking buffer...\n");

	bool full = false;
	for(unsigned int i = buf_len/2; i < buf_len; i++){
		if(buf[i]){
			full = true;
			break;
		}
	}
	if(!full){
		fprintf(stderr, "Failed to recieve to buffer\n");
		free(buf);
		bladerf_trigger_arm(dev, &trig, false, 0, 0);
		trig.role = BLADERF_TRIGGER_ROLE_DISABLED;
		bladerf_close(dev);
		return -1;	
	}
	else{
		FILE *fptr = fopen("./sample.csv", "w");
		for(unsigned int i = 0; i < buf_len - 3; i+=4){
			fprintf(fptr, "%d, %d, %d, %d\n", buf[i], buf[i+1], buf[i+2], buf[i+3]);
		}
		fclose(fptr);
	}

	/* return 0 on success */
	printf("Success!\n");
	free(buf);
	bladerf_trigger_arm(dev, &trig, false, 0, 0);
	trig.role = BLADERF_TRIGGER_ROLE_DISABLED;
	bladerf_close(dev);
	return 0;
}
