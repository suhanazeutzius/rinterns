#include <libbladeRF.h>
#include <stdio.h>
#include "common/bladedevice.h"
#include "pll.h"


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

    /* DO STUFF */
    printf("Master Device PLL State:\n");
    pll_state(master_dev);

    printf("\nSlave Device PLL State:\n");
    pll_state(slave_dev); 

    bladerf_close(master_dev);
    bladerf_close(slave_dev);

    return 0;
}
