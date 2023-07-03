#include <stdio.h>
#include "phaseimposer.h"

int main(){

	int num_samples = 1000;
	printf("Generating test buffers...\n");

	/* allocate int buffers */

	int16_t *buf0 = (int16_t*)malloc(num_samples * 2 * sizeof(int16_t));
	int16_t *buf1 = (int16_t*)malloc(num_samples * 2 * sizeof(int16_t));
	int16_t *buf2 = (int16_t*)malloc(num_samples * 2 * sizeof(int16_t));
	int16_t *buf3 = (int16_t*)malloc(num_samples * 2 * sizeof(int16_t));

	if(!(buf0 && buf1 && buf2 && buf3)){
		fprintf(stderr, "Failed to allocate test buffers\n");
		return -1;
	}
	struct buffers buffers;
	buffers_init(&buffers, &buf0, &buf1, &buf2, &buf3);

	/* fill buffers with test wave */

	complex double z = CMPLX(0.0, 0.0);
	for(int i = 0; i < num_samples - 1; i+=2){
		complex double wave = ccos(z);
		z += CMPLX(1.0, 0.0);

		buf0[i] = (int)creal(wave);
		buf0[i+1] = (int)cimag(wave);

		buf1[i] = (int)creal(wave);
		buf1[i+1] = (int)cimag(wave);

		buf2[i] = (int)creal(wave);
		buf2[i+1] = (int)cimag(wave);

		buf3[i] = (int)creal(wave);
		buf3[i+1] = (int)cimag(wave);
	}

	/* pass to phaseimposer */

	printf("Imposing phase...\n");
	if(phaseimpose_buffers(&buffers, )){
		fprintf(stderr, "Failed to impose phase\n");
		free(buf0);
		free(buf1);
		free(buf2);
		free(buf3);
		return -1;
	}

	/* check phase imposition */
	//TODO

	return 0;
}
