## Cross compilation note: define variable "CROSS" in command line to compiler for arm

## Source Paths
SOURCE_PATH = ../../
INCLUDE_PATH = ../../

COMMON_SOURCE_PATH = $(SOURCE_PATH)/common
COMMON_INCLUDE_PATH = $(INCLUDE_PATH)/common

LOCAL_SOURCE_PATH = ../
LOCAL_INCLUDE_PATH = ../

SOURCES = $(LOCAL_SOURCE_PATH)/phasecalculator.c $(LOCAL_SOURCE_PATH)/phaseimposer.c $(COMMON_SOURCE_PATH)/buffers.c $(COMMON_SOURCE_PATH)/bladedevice.c


## Toolchain Path
ARM_GCC_ROOT_PATH = ../../../gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf


## LibbladeRF Paths
LIBBLADERF_INCLUDE_PATH=$(ARM_GCC_ROOT_PATH)/include
ifndef CROSS
LIBBLADERF_LD_PATH = $(ARM_GCC_ROOT_PATH)/lib64
else
LIBBLADERF_LD_PATH = $(ARM_GCC_ROOT_PATH)/lib
endif



## C Compiler (CC), CC Flags

ifndef CROSS
CC = gcc
else
CC = $(ARM_GCC_ROOT_PATH)/bin/arm-none-linux-gnueabihf-gcc
endif

CFLAGS = -g -W -I $(INCLUDE_PATH) -I $(COMMON_INCLUDE_PATH) -I $(LOCAL_INCLUDE_PATH) -I $(LIBBLADERF_INCLUDE_PATH)
LFLAGS = -L:$(LIBBLADERF_LD_PATH) -l:libbladeRF.so -l:libbladeRF.so.2 -lm



## test phase calculator
calculator: $(SOURCES) Makefile test_calculator.c
	@$(CC) $(CFLAGS) $(SOURCES) test_calculator.c -o ./test $(LFLAGS)

## test phase imposer
imposer: $(SOURCES) Makefile test_imposer.c
	@$(CC) $(CFLAGS) $(SOURCES) test_imposer.c -o ./test $(LFLAGS)


## clean build
clean:
	@rm ./test
