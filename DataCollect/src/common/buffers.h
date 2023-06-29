#ifndef _BUFFERS_H_
#define _BUFFERS_H_

#include <libbladeRF.h>

struct buffers{
    int16_t **buf0;
    int16_t **buf1;
    int16_t **buf2;
    int16_t **buf3;
    int buf_size;
};

void buffers_init(struct buffers *buffers, int16_t **buf0, int16_t **buf1, int16_t **buf2, int16_t **buf3);
void buffers_free(struct buffers *buffers);

#endif
