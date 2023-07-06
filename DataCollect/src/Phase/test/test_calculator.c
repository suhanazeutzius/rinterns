#include <stdio.h>
#include <stdlib.h>
#include <complex.h>
#include "common/buffers.h"
#include "phasecalculator.h"

int main(){

	/* create params */
	int num_samples = 1000;
	int w = 1;
	double phi1 = 0.262, phi2 = 0.524, phi3 = 0.785;

	/* create buffers */
	printf("Initializng buffers...\n");

	int16_t *buf0 = (int16_t *)malloc(2 * sizeof(int16_t) * num_samples);
	int16_t *buf1 = (int16_t *)malloc(2 * sizeof(int16_t) * num_samples);
	int16_t *buf2 = (int16_t *)malloc(2 * sizeof(int16_t) * num_samples);
	int16_t *buf3 = (int16_t *)malloc(2 *sizeof(int16_t) * num_samples);
	struct buffers bufs;
	buffers_init(&bufs, &buf0, &buf1, &buf2, &buf3);

	if(!(buf0 && buf1 && buf2 && buf3)){
		fprintf(stderr, "Failed to allocate buffers.\n");
		return -1;
	}
	bufs.buf_size = num_samples;

	/* fill buffers with waves */
	printf("Filling buffers...\n");

	for(int i = 0, t = 0; i < num_samples - 1; i+=2, t++){
		double complex z = CMPLX(w * t, 0.0);
        double complex wave = 2048 * ccos(z);

		double complex wave0 = wave; 
		double complex wave1 = cexp(CMPLX(phi1, 0.0)) * wave;
		double complex wave2 = cexp(CMPLX(phi2, 0.0)) * wave;
		double complex wave3 = cexp(CMPLX(phi3, 0.0)) * wave;

		buf0[i] = (int16_t) creal(wave0);
		buf0[i+1] = (int16_t) cimag(wave0);

		buf1[i] = (int16_t) creal(wave1);
		buf1[i+1] = (int16_t) cimag(wave1);

		buf2[i] = (int16_t) creal(wave2);
		buf2[i+1] = (int16_t) cimag(wave2);

		buf3[i] = (int16_t) creal(wave3);
		buf3[i+1] = (int16_t) cimag(wave3);
	}

	/* pass buffers to calculator */
	printf("Calculating phases...\n");

	struct delta_phase phases;
	if(phasecalculator_buffers(&bufs, &phases)){
		fprintf(stderr, "Failed to calculate phase from buffers\n");
		buffers_free(&bufs);
		return -1;
	}

	/* compare phases to theoretical */
	printf("Comparing phases...\n");

	printf("Expected Phases\n");
	printf("%f, %f, %f, %f\n", 0.0, phi1, phi2, phi3);
	printf("Actual:\n");
	printf("%f, %f, %f, %f\n", phases.delta_phase0, phases.delta_phase1, phases.delta_phase2, phases.delta_phase3);

	buffers_free(&bufs);
	return 0;
}
