## Cross compilation note: define variable "CROSS" in command line to compiler for arm

## Source Paths
SOURCE_PATH = ../../
INCLUDE_PATH = ../../

COMMON_SOURCE_PATH = $(SOURCE_PATH)/common
COMMON_INCLUDE_PATH = $(INCLUDE_PATH)/common

LOCAL_SOURCE_PATH = ../
LOCAL_INCLUDE_PATH = ../

SOURCES = $(LOCAL_SOURCE_PATH)/channel.c $(LOCAL_SOURCE_PATH)/clock.c $(LOCAL_SOURCE_PATH)/sampler.c $(LOCAL_SOURCE_PATH)/syncstream.c $(LOCAL_SOURCE_PATH)/trigger.c $(LOCAL_SOURCE_PATH)/pll.c $(COMMON_SOURCE_PATH)/buffers.c $(COMMON_SOURCE_PATH)/bladedevice.c


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

CFLAGS = -g -W -pthread -I $(INCLUDE_PATH) -I $(COMMON_INCLUDE_PATH) -I $(LOCAL_INCLUDE_PATH) -I $(LIBBLADERF_INCLUDE_PATH)
LFLAGS = -L:$(LIBBLADERF_LD_PATH) -l:libbladeRF.so -l:libbladeRF.so.2



## test channel
channel: $(SOURCES) Makefile test_channel.c
	@$(CC) $(CFLAGS) $(SOURCES) $(LFLAGS) test_channel.c -o ./test

## test clock
clock: $(SOURCES) Makefile test_clock.c
	@$(CC) $(CFLAGS) $(SOURCES) $(LFLAGS) test_clock.c -o ./test

## test trigger
trigger: $(SOURCES) Makefile test_trigger.c
	@$(CC) $(CFLAGS) $(SOURCES) $(LFLAGS) test_trigger.c -o ./test

## test trigger single
trigger_single: $(SOURCES) Makefile test_trigger_single.c
	@$(CC) $(CFLAGS) $(SOURCES) $(LFLAGS) test_trigger_single.c -o ./test

## test trigger multi
trigger_multi: $(SOURCES) Makefile test_trigger_multi.c
	@$(CC) $(CFLAGS) $(SOURCES) $(LFLAGS) test_trigger_multi.c -o ./test

## test trigger syncstream (single slave)
trigger_syncstream: $(SOURCES) Makefile test_trigger_syncstream.c
	@$(CC) $(CFLAGS) $(SOURCES) $(LFLAGS) test_trigger_syncstream.c -o ./test

## test trigger syncstream (single master)
trigger_syncstream_master: $(SOURCES) Makefile test_trigger_syncstream.c
	@$(CC) $(CFLAGS) $(SOURCES) $(LFLAGS) test_trigger_syncstream_master.c -o ./test

## test syncstream
syncstream: $(SOURCES) Makefile test_syncstream.c
	@$(CC) $(CFLAGS) $(SOURCES) $(LFLAGS) test_syncstream.c -o ./test

## test sampler
sampler: $(SOURCES) Makefile test_sampler.c
	@$(CC) $(CFLAGS) $(SOURCES) $(LFLAGS) test_sampler.c -o ./test

## test pll
lowlevel: $(SOURCES) Makefile test_lowlevel.c
	@$(CC) $(CFLAGS) $(SOURCES) $(LFLAGS) test_lowlevel.c -o ./test

## test all
all: $(SOURCES) Makefile test_all.c
	@$(CC) $(CFLAGS) $(SOURCES) $(LFLAGS) test_all.c -o ./test


## clean build
clean:
	@rm ./test
