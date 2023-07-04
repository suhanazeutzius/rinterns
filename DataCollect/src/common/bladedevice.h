#ifndef _BLADEDEVICE_H_
#define _BLADEDEVICE_H_

#include <libbladeRF.h>
#include <stdio.h>

static const char *MASTER_ID = "*:serial=8708f9acef41465c8f457fdc94526d93";
static const char *SLAVE_ID = "*:serial=b81fded3527b42adbd09f31345c60584";

int open_devices(struct bladerf **master, struct bladerf **slave);

#endif
