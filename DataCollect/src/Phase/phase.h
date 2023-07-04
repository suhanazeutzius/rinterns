#ifndef _PHASE_H_
#define _PHASE_H_

enum phase_error{
	BUFFERS_NULL_ERROR = -1,
	BUFFERS_EMPTY_ERROR = -2,
	DELTA_PHASE_NULL_ERROR = -3,
	CSV_PARSER_ERROR = -4,
};


/* delta phase double are radians */

struct delta_phase{
    double delta_phase0;
    double delta_phase1;
    double delta_phase2;
    double delta_phase3;
};

#endif
