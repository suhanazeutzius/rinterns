#include "bladedevice.h"

/**
 * open both devices
 *
 * @param struct bladerf **master -- master device
 * @param struct bladerf **slave -- slave device
 * @return int -- 0 on success, -1 on failure (timeout)
 *
 * @brief waits for positive (0) result from device opening;
 * TODO: implement a timeout (add to params list)
 **/
int open_devices(struct bladerf **master, struct bladerf **slave){

	int status;

	do{ status = bladerf_open(master, MASTER_ID); } while(status != 0);
	do{ status = bladerf_open(slave, SLAVE_ID); } while(status != 0);

	return 0;
}
