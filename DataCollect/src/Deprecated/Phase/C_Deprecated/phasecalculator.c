#include "phasecalculator.h"


/**
 * Calculate phase delta between each channel
 *
 * @param struct buffers *buffers -- sample buffers for 4 channels
 * @param struct delta_phase *delta_phase -- delta phase for each channel (output)
 * @return int -- return 0 on success, phase_error on failure
 *
 * @brief calculates running averages for a sum and difference vector for channels 1-3
 * relative to channel 0, takes the ratio of difference to sum average for each, then
 * uses the equation phase = 2arctan(-imag{diff/sum})
 **/
int phasecalculator_buffers(struct buffers *buffers, struct delta_phase *delta_phase){

	/* check input parameters */

	if(!buffers){
		fprintf(stderr, "Failed to calculate phase delta: Buffers NULL\n");
		return BUFFERS_NULL_ERROR;
	}
	if(!delta_phase){
		fprintf(stderr, "Failed to calculate phase delta: Delta Phase NULL\n");
		return DELTA_PHASE_NULL_ERROR;
	}
	if(!(buffers->buf_size)){
		fprintf(stderr, "Failed to calculate phase delta: Buffers empty\n");
		return BUFFERS_EMPTY_ERROR;
	}


	/* calculate avg sum and difference for bufs 1-3 and buf0 */

	int cnt = 0;
	int32_t sumI1_avg = 0;
	int32_t sumQ1_avg = 0;
	int32_t diffI1_avg = 0;
	int32_t diffQ1_avg = 0;

	int32_t sumI2_avg = 0;
	int32_t sumQ2_avg = 0;
	int32_t diffI2_avg = 0;
	int32_t diffQ2_avg = 0;

	int32_t sumI3_avg = 0;
	int32_t sumQ3_avg = 0;
	int32_t diffI3_avg = 0;
	int32_t diffQ3_avg = 0;

	int32_t sumI, diffI, sumQ, diffQ;

	for(int i = 0; i < buffers->buf_size - 1; i+=2, cnt+=1){

		/* ith sum & diff for I,Q */
		sumI = (*(buffers->buf0))[i] + (*(buffers->buf1))[i];
		diffI = (*(buffers->buf0))[i] - (*(buffers->buf1))[i];
		sumQ = (*(buffers->buf0))[i+1] + (*(buffers->buf1))[i+1];
		diffQ = (*(buffers->buf0))[i+1] + (*(buffers->buf1))[i+1];

		/* add sum & diff to averages */
		sumI1_avg = ((sumI1_avg*cnt) + sumI) / (cnt+1);
		sumQ1_avg = ((sumQ1_avg*cnt) + sumQ) / (cnt+1);
		diffI1_avg = ((diffI1_avg*cnt) + diffI) / (cnt+1);
		diffQ1_avg = ((diffQ1_avg*cnt) + diffQ) / (cnt+1);

		/* ith sum & diff for I,Q */
		sumI = (*(buffers->buf0))[i] + (*(buffers->buf2))[i];
		diffI = (*(buffers->buf0))[i] - (*(buffers->buf2))[i];
		sumQ = (*(buffers->buf0))[i+1] + (*(buffers->buf2))[i+1];
		diffQ = (*(buffers->buf0))[i+1] + (*(buffers->buf2))[i+1];
		/* add sum & diff to averages */
		sumI2_avg = ((sumI2_avg*cnt) + sumI) / (cnt+1);
		sumQ2_avg = ((sumQ2_avg*cnt) + sumQ) / (cnt+1);
		diffI2_avg = ((diffI2_avg*cnt) + diffI) / (cnt+1);
		diffQ2_avg = ((diffQ2_avg*cnt) + diffQ) / (cnt+1);

		/* ith sum & diff for I,Q */
		sumI = (*(buffers->buf0))[i] + (*(buffers->buf3))[i];
		diffI = (*(buffers->buf0))[i] - (*(buffers->buf3))[i];
		sumQ = (*(buffers->buf0))[i+1] + (*(buffers->buf3))[i+1];
		diffQ = (*(buffers->buf0))[i+1] + (*(buffers->buf3))[i+1];
		/* add sum & diff to averages */
		sumI3_avg = ((sumI3_avg*cnt) + sumI) / (cnt+1);
		sumQ3_avg = ((sumQ3_avg*cnt) + sumQ) / (cnt+1);
		diffI3_avg = ((diffI3_avg*cnt) + diffI) / (cnt+1);
		diffQ3_avg = ((diffQ3_avg*cnt) + diffQ) / (cnt+1);
	}

	/* convert avgs to complex */

	double complex csum1_avg = CMPLX((double)sumI1_avg, (double)sumQ1_avg);
	double complex cdiff1_avg = CMPLX((double)diffI1_avg, (double)diffQ1_avg);

	double complex csum2_avg = CMPLX((double)sumI2_avg, (double)sumQ2_avg);
	double complex cdiff2_avg = CMPLX((double)diffI2_avg, (double)diffQ2_avg);

	double complex csum3_avg = CMPLX((double)sumI3_avg, (double)sumQ3_avg);
	double complex cdiff3_avg = CMPLX((double)diffI3_avg, (double)diffQ3_avg);

	/* take diff to sum ratio */

	double complex r1 = cdiff1_avg / csum1_avg;
	double complex r2 = cdiff2_avg / csum2_avg;
	double complex r3 = cdiff3_avg / csum3_avg;

    printf("%f, %f, %f\n", creal(r1), creal(r2), creal(r3));
    printf("%f, %f, %f\n", cimag(r1), cimag(r2), cimag(r3));

	/* get phase */

	double phase1 = 2 * atan(-1.0 * cimag(r1));
	double phase2 = 2 * atan(-1.0 * cimag(r2));
	double phase3 = 2 * atan(-1.0 * cimag(r3));

	/* convert from complex & store */

	delta_phase->delta_phase0 = 0.0;
	delta_phase->delta_phase1 = phase1;
	delta_phase->delta_phase2 = phase2;
	delta_phase->delta_phase3 = phase3;

	/* return 0 on success */
	return 0;
}





/**
 * Calculate phase delta between each channel using csv file
 *
 * @param char *filename -- csv file name
 * @param struct delta_phase *delta_phase -- delta phase for each channel (output)
 * @return int -- return 0 on success, phase_error on failure
 *
 * @brief opens a file and converts file values into buffers & calls phasecalculator_buffers
 **/
int phasecalculator_csv(char *filename, struct delta_phase *delta_phase){

	struct buffers buffers;

	/* get buffers from csv */

	if(csv_to_buffers(filename, &buffers)){
		fprintf(stderr, "Failed to calculate phases: Csv converter failed\n");
		return CSV_PARSER_ERROR;
	}

	/* get phase from buffers */

	int ret = phasecalculator_buffers(&buffers, delta_phase);
	buffers_free(&buffers);
	return ret;
}
