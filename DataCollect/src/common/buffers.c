#include "buffers.h"


/**
 * initialize a buffers struct
 *
 * @param struct buffers *buffers -- pointer to buffers struct to init
 * @param int16_t **buf0..3 -- pointer to buffers to be contained by buffers struct
 * @return none
 *
 **/
void buffers_init(struct buffers *buffers, int16_t **buf0, int16_t **buf1, int16_t **buf2, int16_t **buf3){

    buffers->buf0 = buf0;
    buffers->buf1 = buf1;
    buffers->buf2 = buf2;
    buffers->buf3 = buf3;
    buffers->buf_size = 0;
    return;
}





/**
 * free a buffers struct associated buffers
 *
 * @param struct buffers *buffers -- pointer to buffers struct to free
 * @return none
 *
 **/
void buffers_free(struct buffers *buffers){

    if(*(buffers->buf0)) free(*(buffers->buf0));
    if(*(buffers->buf1)) free(*(buffers->buf1));
    if(*(buffers->buf2)) free(*(buffers->buf2));
    if(*(buffers->buf3)) free(*(buffers->buf3));

    *(buffers->buf0) = NULL;
    *(buffers->buf1) = NULL;
    *(buffers->buf2) = NULL;
    *(buffers->buf3) = NULL;

    buffers->buf_size = 0;

    return;
}
