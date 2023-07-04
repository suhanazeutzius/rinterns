#include <stdio.h>
#include "common/buffers.h"
#include "phasecalculator.h"
#include "phaseimposer.h"

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

	if(!(buf0 && buf1 && buf2 && buf3)){
		fprintf(stderr, "Failed to allocate buffers.\n");
		return -1;
	}

	buffers_init(&bufs, &buf0, &buf1, &buf2, &buf3);


	/* fill buffers with waves */
	printf("Filling buffers...\n");

	for(int i = 0, t = 0; i < num_samples - 1; i+=2, t++){
		double complex z0 = CMPLX(w * t, w * t);
		double complex z1 = CMPLX(w * t + phi1, w * t + phi1);
		double complex z2 = CMPLX(w * t + phi2, w * t + phi2);
		double complex z3 = CMPLX(w * t + phi3, w * t + phi3);

		double complex wave0 = ccos(z0);
		double complex wave1 = ccos(z1);
		double complex wave2 = ccos(z2);
		double complex wave3 = ccos(z3);

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

	/* pass delta phase to imposer */
	printf("Imposing phases...\n");
	if(phaseimpose_buffers(&bufs, phases)){
		fprintf(stderr, "Failed to impose phase on buffers\n");
		buffers_free(&bufs);
		return -1;
	}

	/* pass buffers back to calculator */
	printf("Calculating new phases...\n");
	if(phasecalculator_buffers(&bufs, &phases)){
		fprintf(stderr, "Failed to calculate phase from buffers\n");
		buffers_free(&bufs);
		return -1;
	}

	/* check phases */
	printf("Checking new phases...\n");
	printf("Expected:\n");
	printf("%f, %f, %f, %f\n", 0.0, phi1, phi2, phi3);
	printf("Actual:\n");
	printf("%f, %f, %f, %f\n", phases.delta_phase0, phases.delta_phase1, phases.delta_phase2, phases.delta_phase3);

	buffers_free(&bufs);
	return 0;
}
