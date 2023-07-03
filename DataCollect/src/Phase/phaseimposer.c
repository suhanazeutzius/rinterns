#include "phaseimposer.h"

int main(){
	return 0;
}

/**
 * Imposes a delta phase onto sample buffers
 *
 * @param struct buffers *buffers -- buffers to impose phase on
 * @param struct delta_phase -- delta phase for 4 channels
 * @return int -- 0 on success, phaseimpose_error on failure
 *
 * @brief temporarily converts sample buffers into complex doubles by
 * de-interleaving and typecasting, creates complex exponentials out of
 * delta_phase members, multiplies complex samples by exponentials, then
 * re-casts to integers before storing back in buffers
 **/
int phaseimpose_buffers(struct buffers *buffers, struct delta_phase delta_phase){

	/* check input parameters */

	if(!buffers){
		fprintf(stderr, "Failed to impose phase on buffers: Buffers pointer is NULL\n");
		return BUFFERS_NULL_ERROR;
	}
	if(!(buffers->buf_size)){
		fprintf(stderr, "Failed to impose phase on buffers: Buffers empty\n");
		return BUFFERS_EMPTY_ERROR;
		return -1;
	}

	/* multiply samples by complex exponential (e^j*phase) */

	/* calc phase exponential */
	complex double cp0 = cexp(I * delta_phase.delta_phase0);
	complex double cp1 = cexp(I * delta_phase.delta_phase1);
	complex double cp2 = cexp(I * delta_phase.delta_phase2);
	complex double cp3 = cexp(I * delta_phase.delta_phase3);

	for(int i = 0; i < buffers->buf_size - 1; i+=2){
		/* convert samples to complex */
		complex double cb0 = CMPLX((double)(*(buffers->buf0))[i], (double)(*(buffers->buf0))[i+1]);
		complex double cb1 = CMPLX((double)(*(buffers->buf1))[i], (double)(*(buffers->buf1))[i+1]);
		complex double cb2 = CMPLX((double)(*(buffers->buf2))[i], (double)(*(buffers->buf2))[i+1]);
		complex double cb3 = CMPLX((double)(*(buffers->buf3))[i], (double)(*(buffers->buf3))[i+1]);

		/* multiply complex samples by cmplx exp && store into buffers */
		(*(buffers->buf0))[i] = (int) creal(cb0 * cp0);
		(*(buffers->buf0))[i+1] = (int) cimag(cb0 * cp0);

		(*(buffers->buf1))[i] = (int) creal(cb1 * cp1);
		(*(buffers->buf1))[i+1] = (int) cimag(cb1 * cp1);

		(*(buffers->buf2))[i] = (int) creal(cb2 * cp2);
		(*(buffers->buf2))[i+1] = (int) cimag(cb2 * cp2);

		(*(buffers->buf3))[i] = (int) creal(cb3 * cp3);
		(*(buffers->buf3))[i+1] = (int) cimag(cb3 * cp3);
	}

	/* return 0 on success */
	return 0;

}





/**
 * Imposes a delta phsae onto csv file
 *
 * @param char *filename -- csv file to impose phase on
 * @param struct delta_phase delta_phase -- delta phase for 4 channels
 * @return int -- return 0 on success, -1 on failure
 *
 * @brief opens a file and converts file parameters into buffers & calls
 * phaseimpose_buffers, then re-writes buffers to csv file
 **/
int phaseimpose_csv(char *filename, struct delta_phase delta_phase){

    /* TODO */
}
