## Cross compilation note: define variable "CROSS" in command line to compiler for arm

## Paths / Sources
SOURCE_PATH = ../
INCLUDE_PATH = ../

SOURCES = $(SOURCE_PATH)/channel.c $(SOURCE_PATH)/clock.c $(SOURCE_PATH)/sampler.c $(SOURCE_PATH)/syncstream.c $(SOURCE_PATH)/trigger.c




## C Compiler / Flags

ifndef CROSS

CC = gcc -g -W -I $(INCLUDE_PATH)
LFLAGS = -l:libbladeRF.so -l:libbladeRF.so.2

else

ARM_GCC_ROOT_PATH = ../../../gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf

LIBBLADERF_LD_PATH=$(ARM_GCC_ROOT_PATH)/lib64
LIBBLADERF_INCLUDE_PATH=$(ARM_GCC_ROOT_PATH)/include

COMP = $(ARM_GCC_ROOT_PATH)/bin/arm-none-linux-gnueabihf-gcc
CFLAGS = -g -W -I $(INCLUDE_PATH) -I $(LIBBLADERF_INCLUDE_PATH)
CC= $(COMP) $(CFLAGS)

LFLAGS = -l:$(LIBBLADERF_LD_PATH)/libbladeRF.so -l:$(LIBBLADERF_LD_PATH)/libbladeRF.so.2

endif






## test channel
channel: $(SOURCES) Makefile test_channel.c
	@$(CC) $(SOURCES) $(LFLAGS) test_channel.c -o ./test

## test clock
clock: $(SOURCES) Makefile test_clock.c
	@$(CC) $(SOURCES) $(LFLAGS) test_clock.c -o ./test

## test trigger
trigger: $(SOURCES) Makefile test_trigger.c
	@$(CC) $(SOURCES) $(LFLAGS) test_trigger.c -o ./test

## test syncstream
syncstream: $(SOURCES) Makefile test_syncstream.c
	@$(CC) $(SOURCES) $(LFLAGS) test_syncstream.c -o ./test

## test sampler
sampler: $(SOURCES) Makefile test_sampler.c
	@$(CC) $(SOURCES) $(LFLAGS) test_sampler.c -o ./test

## test all
all: $(SOURCES) Makefile test_all.c
	@$(CC) $(SOURCES) $(LFLAGS) test_all.c -o ./test


## clean build
clean:
	@rm ./test
