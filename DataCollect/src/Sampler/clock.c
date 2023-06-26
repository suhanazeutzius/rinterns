#include "clock.h"

/**
 * Initialize clock sharing
 *
 * @param struct bladerf *master_dev -- master device
 * @param struct bladerf *slave_dev -- slave device
 * @return int -- return 0 on success, bladerf error code on failure
 *
 * @brief master device will output a 38.4MHz reference clock on the SMB
 * port, and the slave device will expect a 38.4MHz reference clock on its
 * SMB input port
 **/
int clock_init(struct bladerf *master_dev, struct bladerf *slave_dev){
	int status;

	/* configure master clock output (auto frequency=38.4MHz) */
	status = bladerf_set_smb_mode(master_dev, BLADERF_SMB_MODE_OUTPUT);
	if(status != 0){
		fprintf(stderr, "Failed to set master device SMB output: %s\n", bladerf_strerror(status));
		return status;
	}

	/* configure slave clock input */
	bladerf_set_smb_mode(slave_dev, BLADERF_SMB_MODE_INPUT);
	if(status != 0){
		fprintf(stderr, "Failed to set slave device SMB input: %s\n", bladerf_strerror(status));
		return status;
	}

	return 0;
}