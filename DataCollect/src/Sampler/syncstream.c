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

    status = bladerf_sync_config(master_dev, BLADERF_RX_X1, BLADERF_FORMAT_SC16_Q11, st_config.num_buffers, st_config.buffer_size, st_config.num_transfers, st_config.timeout_ms);
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

    /* check master/slave buffers */

    if(master_buffer){
        fprintf(stderr, "Warning: allocating to non-null master buffer, data could be lost\n");
        free(master_buffer);
        master_buffer = NULL;
        master_buffer_len = 0;
    }
    if(slave_buffer){
        fprintf(stderr, "Warning: allocating to non-null slave buffer, data could be lost\n");
        free(slave_buffer);
        slave_buffer = NULL;
        master_buffer_len = 0;
    }

    /* allocate master/slave buffers */
    const unsigned int buf_size = st_config.num_samples * 2 * 2 * sizeof(int16_t);

    master_buffer = (int16_t*)malloc(buf_size);
    if(!master_buffer){
        fprintf(stderr, "Failed to allocate master buffer: %s\n", bladerf_strerror(BLADERF_ERR_MEM));
        return BLADERF_ERR_MEM;
    }
    master_buffer_len = (unsigned int)(buf_size / sizeof(int16_t));

    slave_buffer = (int16_t*)malloc(buf_size);
    if(!slave_buffer){
        free(master_buffer);
        master_buffer = NULL;
        master_buffer_len = 0;
        slave_buffer = NULL;

        fprintf(stderr, "Failed to allocate slave buffer: %s\n", bladerf_strerror(BLADERF_ERR_MEM));
        return BLADERF_ERR_MEM;
    }
    slave_buffer_len = (unsigned int)(buf_size / sizeof(int16_t));

    /* enable RF front ends */

    status = channel_enable(master_dev);
    if(status != 0) goto exit_free_memory;

    status = channel_enable(slave_dev);
    if(status != 0) goto exit_free_memory;

    /* start stream recieve (master) */

    status = bladerf_sync_rx(master_dev, master_buffer, st_config.num_samples * 2, NULL, st_config.timeout_ms);
    if(status != 0){
        fprintf(stderr, "Failed to start master sync rx stream (memory freed): %s\n", bladerf_strerror(status));
		goto exit_free_memory;
    }
    
    /* start stream recieve (slave) */

    status = bladerf_sync_rx(slave_dev, slave_buffer, st_config.num_samples * 2, NULL, st_config.timeout_ms);
    if(status != 0){
        fprintf(stderr, "Failed to start slave sync rx stream (memory freed): %s\n", bladerf_strerror(status));
		goto exit_free_memory;
    }

    /* return 0 on success */

    return 0;

exit_free_memory:
	free(slave_buffer);
	slave_buffer = NULL;
	slave_buffer_len = 0;

	free(master_buffer);
	master_buffer = NULL;
	master_buffer_len = 0;
	return status;
}





/**
 * handle a sync stream into a csv file
 *
 * @param struct bladerf *master_dev -- master device
 * @param struct bladerf *slave_dev -- slave device
 * @return int -- return 0 on success, bladerf error code on failure
 *
 * @brief recieves from the master and slave buffers and appends to a CSV
 **/
int syncstream_handle_csv(struct bladerf *master_dev, struct bladerf *slave_dev, char *filename){

    /* check buffers */

    if(!master_buffer || !slave_buffer){
        fprintf(stderr, "master/slave Rx Buffers are NULL\n");
        return BLADERF_ERR_MEM;
    }

    /* open file */
    
    FILE *fptr = fopen(filename, "a");
    if(!fptr) return -1;

    /* get number of buffer samples */

    unsigned int num_reads;
    if(master_buffer_len > slave_buffer_len){
        num_reads = slave_buffer_len;
    }
    else{
        num_reads = master_buffer_len;
    }

    for(unsigned int i = 0; i < num_reads-3; i+=4){
        fprintf(fptr, "%d, %d, %d, %d, %d, %d, %d, %d\n", master_buffer[i], master_buffer[i+1], master_buffer[i+2], master_buffer[i+3], slave_buffer[i], slave_buffer[i+1], slave_buffer[i+2], slave_buffer[i+3]);
}

    /* free memory */

    fclose(fptr);
    syncstream_free_buffers();

    return 0;
}





/**
 * handle a syncstream into separate buffers (per channel)
 *
 * @param struct bladerf *master_dev -- master device
 * @param struct bladerf *slave_dev -- slave device
 * @param struct buffers *buffers -- 4 channels interleaved IQ data & size of buffers
 * @return int -- 0 on success, -1 or balderf error code on failure
 *
 * @brief uses master/slave buffers & lengths to separate into 4 channels
 **/
int syncstream_handle_buffers(struct bladerf *master_dev, struct bladerf *slave_dev, struct buffers *buffers){

    
    /* check buffers */

    if(!master_buffer || !slave_buffer){
        fprintf(stderr, "master/slave Rx Buffers are NULL\n");
        return BLADERF_ERR_MEM;
    }
 
    /* get per-device buffer length */

    int num_samples;
    if(master_buffer_len > slave_buffer_len){
        num_samples = slave_buffer_len / 2;
    }
    else{
        num_samples = master_buffer_len / 2;
    }

    /* allocate buffers */

    *(buffers->buf0) = (int16_t*)malloc(num_samples * sizeof(int16_t));
    *(buffers->buf1) = (int16_t*)malloc(num_samples * sizeof(int16_t));
    *(buffers->buf2) = (int16_t*)malloc(num_samples * sizeof(int16_t));
    *(buffers->buf3) = (int16_t*)malloc(num_samples * sizeof(int16_t));
    buffers->buf_size = (num_samples * sizeof(int16_t));

    if(!(*(buffers->buf0) && *(buffers->buf1) && *(buffers->buf2) && *(buffers->buf3))){
        fprintf(stderr, "Failed to allocate buffers\n");
        buffers_free(buffers);
        syncstream_free_buffers();
        return -1;
    }

    /* recieve to buffers */

    for(int i = 0, j = 0; i < num_samples*2; i+=4, j+=2){
        (*(buffers->buf0))[j] = master_buffer[i];
        (*(buffers->buf0))[j+1] = master_buffer[i+1];

        (*(buffers->buf1))[j] = master_buffer[i+2];
        (*(buffers->buf1))[j+1] = master_buffer[i+3];

        (*(buffers->buf2))[j] = slave_buffer[i];
        (*(buffers->buf2))[j+1] = slave_buffer[i+1];

        (*(buffers->buf3))[j] = slave_buffer[i+2];
        (*(buffers->buf3))[j+1] = slave_buffer[i+3];
    }

    /* free memory */

    syncstream_free_buffers();
    return 0;
}





/**
 * free master/slave buffers
 *
 * @param none
 * @return none
 *
 * @brief free buffers, set lengths to 0, set
 * pointers to NULL
 **/
void syncstream_free_buffers(void){
    free(master_buffer);
    free(slave_buffer);
    master_buffer = NULL;
    slave_buffer = NULL;
    master_buffer_len = 0;
    slave_buffer_len = 0;
}
