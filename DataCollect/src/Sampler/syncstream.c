#include "syncstream.h"


/**
 * initialize and begin a sync rx stream
 *
 * @param struct bladerf *master_dev -- master device
 * @param struct bladerf *slave_dev -- slave device
 * @param struct stream_config st_config -- stream configuration parameter struct
 * @return int -- returns 0 on success, bladerf error code on failure
 *
 * @brief calls bladerf_sync_config() and bladerf_sync_rx() using st_config parameters
 * Note: enusre that timeout_ms parameter leaves enough time to cover latency between
 * this call and call to trigger_fire()
 **/
int syncstream_init(struct bladerf *master_dev, struct bladerf *slave_dev, struct stream_config st_config){

    int status;

    /* configure sync stream (master) */

    status = bladerf_sync_config(master_dev, BLADERF_RX_X2, BLADERF_FORMAT_SC16_Q11, st_config.num_buffers, st_config.buffer_size, st_config.num_transfers, st_config.timeout_ms);
    if(status != 0){
        fprintf(stderr, "Failed to configure master stream: %s\n", bladerf_strerror(status));
        return status;
    }

    /* configure sync stream (slave) */

    status = bladerf_sync_config(slave_dev, BLADERF_RX_X2, BLADERF_FORMAT_SC16_Q11, st_config.num_buffers, st_config.buffer_size, st_config.num_transfers, st_config.timeout_ms);
    if(status != 0){
        fprintf(stderr, "Failed to configure slave stream: %s\n", bladerf_strerror(status));
        return status;
    }

    /* enable RF front ends */

    status = channel_enable(master_dev);
    if(status != 0) return status;

    status = channel_enable(slave_dev);
    if(status != 0) return status;

    /* check master/slave buffers */

    if(master_buffer){
        fprintf(stderr, "Warning: allocating to non-null master buffer, data could be lost\n");
        free(master_buffer);
        master_buffer = NULL;
    }
    if(slave_buffer){
        fprintf(stderr, "Warning: allocating to non-null slave buffer, data could be lost\n");
        free(slave_buffer);
        slave_buffer = NULL;
    }

    /* allocate master/slave buffers */

    master_buffer = (int16_t*)malloc(st_config.num_samples * 2 * 1 * sizeof(int16_t));
    if(!master_buffer){
        fprintf(stderr, "Failed to allocate master buffer: %s\n", bladerf_strerror(BLADERF_ERR_MEM));
        return BLADERF_ERR_MEM;
    }

    slave_buffer = (int16_t*)malloc(st_config.num_samples * 2 * 1 * sizeof(int16_t));
    if(!slave_buffer){
        free(master_buffer);
        master_buffer = NULL;
        slave_buffer = NULL;

        fprintf(stderr, "Failed to allocate slave buffer: %s\n", bladerf_strerror(BLADERF_ERR_MEM));
        return BLADERF_ERR_MEM;
    }

    /* start stream recieve (master) */

    status = bladerf_sync_rx(master_dev, master_buffer, st_config.num_samples, NULL, st_config.timeout_ms);
    if(status != 0){
        free(slave_buffer);
        slave_buffer = NULL;

        free(master_buffer);
        master_buffer = NULL;

        fprintf(stderr, "Failed to start master sync rx stream (memory freed): %s\n", bladerf_strerror(status));
        return status;
    }
    
    /* start stream recieve (slave) */

    status = bladerf_sync_rx(slave_dev, slave_buffer, st_config.num_samples, NULL, st_config.timeout_ms);
    if(status != 0){
        free(slave_buffer);
        slave_buffer = NULL;

        free(master_buffer);
        master_buffer = NULL;

        fprintf(stderr, "Failed to start slave sync rx stream (memory freed): %s\n", bladerf_strerror(status));
        return status;
    }

    /* return 0 on success */

    return 0;
}





/**
 * handle a sync stream
 *
 * @param struct bladerf *master_dev -- master device
 * @param struct bladerf *slave_dev -- slave device
 * @return int -- return 0 on success, bladerf error code on failure
 *
 * @brief recieves from the master and slave buffers and appends to a CSV
 **/
int syncstream_handle(struct bladerf *master_dev, struct bladerf *slave_dev){

    /* check buffers */

    if(!master_buffer || !slave_buffer){
        fprintf(stderr, "master/slave Rx Buffers are NULL\n");
        return BLADERF_ERR_MEM;
    }

    /* open file */
    
    FILE *fptr = fopen("sample.csv", "a");
    if(!fptr) return -1;

    int num_reads;
    if(sizeof(master_buffer)/sizeof(int16_t) > sizeof(slave_buffer)/sizeof(int16_t)){
        num_reads = sizeof(slave_buffer)/sizeof(int16_t);
    }
    else{
        num_reads = sizeof(master_buffer)/sizeof(int16_t);
    }

    for(int i = 0; i < num_reads-3; i+=4){
        fprintf(fptr, "%d, %d, %d, %d, %d, %d, %d, %d\n", master_buffer[i], master_buffer[i+1], master_buffer[i+2], master_buffer[i+3], slave_buffer[i], slave_buffer[i+1], slave_buffer[i+2], slave_buffer[i+3]);
}

    fclose(fptr);
    free(master_buffer);
    free(slave_buffer);
    master_buffer = NULL;
    slave_buffer = NULL;

    return 0;
}
