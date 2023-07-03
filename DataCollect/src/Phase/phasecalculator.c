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

	for(int i = 0; i < buffers->buf_size - 1; i+=2){
		sumI1_avg = (sumI1_avg*cnt + ((*(buffers->buf0))[i]  + (*(buffers->buf1))[i])) / cnt+1;
		sumQ1_avg = (sumQ1_avg*cnt + ((*(buffers->buf0))[i+1]  + (*(buffers->buf1))[i+1])) / cnt+1;
		diffI1_avg = (sumI1_avg*cnt + ((*(buffers->buf0))[i]  + (*(buffers->buf1))[i])) / cnt+1;
		diffQ1_avg = (sumQ1_avg*cnt + ((*(buffers->buf0))[i+1]  + (*(buffers->buf1))[i+1])) / cnt+1;

		sumI2_avg = (sumI2_avg*cnt + ((*(buffers->buf0))[i]  + (*(buffers->buf2))[i])) / cnt+1;
		sumQ2_avg = (sumQ2_avg*cnt + ((*(buffers->buf0))[i+1]  + (*(buffers->buf2))[i+1])) / cnt+1;
		diffI2_avg = (sumI2_avg*cnt + ((*(buffers->buf0))[i]  + (*(buffers->buf2))[i])) / cnt+1;
		diffQ2_avg = (sumQ2_avg*cnt + ((*(buffers->buf0))[i+1]  + (*(buffers->buf2))[i+1])) / cnt+1;

		sumI3_avg = (sumI3_avg*cnt + ((*(buffers->buf0))[i]  + (*(buffers->buf3))[i])) / cnt+1;
		sumQ3_avg = (sumQ3_avg*cnt + ((*(buffers->buf0))[i+1]  + (*(buffers->buf3))[i+1])) / cnt+1;
		diffI3_avg = (sumI3_avg*cnt + ((*(buffers->buf0))[i]  + (*(buffers->buf3))[i])) / cnt+1;
		diffQ3_avg = (sumQ3_avg*cnt + ((*(buffers->buf0))[i+1]  + (*(buffers->buf3))[i+1])) / cnt+1;
	}

	/* convert avgs to complex */

	complex double sum1_avg = CMPLX(sumI1_avg, sumQ1_avg);
	complex double diff1_avg = CMPLX(diffI1_avg, diffQ1_avg);

	complex double sum2_avg = CMPLX(sumI2_avg, sumQ2_avg);
	complex double diff2_avg = CMPLX(diffI2_avg, diffQ2_avg);

	complex double sum1_avg = CMPLX(sumI3_avg, sumQ3_avg);
	complex double diff1_avg = CMPLX(diffI3_avg, diffQ3_avg);

	/* take diff to sum ratio */

	complex double r1 = diff1_avg / sum1_avg;
	complex double r2 = diff2_avg / sum2_avg;
	complex double r3 = diff3_avg / sum3_avg;

	/* get phase */

	complex double cphase1 = 2 * catan(-1.0 * cimag(r1));
	complex double cphase2 = 2 * catan(-1.0 * cimag(r2));
	complex double cphase3 = 2 * catan(-1.0 * cimag(r3));

	/* convert from complex & store */

	delta_phase->delta_phase0 = 0.0;
	delta_phase->delta_phase1 = creal(cphase1);
	delta_phase->delta_phase2 = creal(cphase2);
	delta_phase->delta_phase3 = creal(cphase3);

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

	struct buffers;

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
