## Cross compilation note: define variable "CROSS" in command line to compiler for arm

## Source Paths
SOURCE_PATH = ..
INCLUDE_PATH = ..

COMMON_SOURCE_PATH = $(SOURCE_PATH)/common
COMMON_INCLUDE_PATH = $(INCLUDE_PATH)/common

LOCAL_SOURCE_PATH = .
LOCAL_INCLUDE_PATH = .

SOURCES =


## Toolchain Path
ARM_GCC_ROOT_PATH = $(SOURCE_PATH)/../gcc-arm-10.3-2021.07-x86_64-arm-none-linux-gnueabihf


## VSG60 Paths
VSG60_INCLUDE_PATH=$(ARM_GCC_ROOT_PATH)/include
ifndef CROSS
VSG60_LD_PATH = $(ARM_GCC_ROOT_PATH)/lib64
else
VSG60_LD_PATH = $(ARM_GCC_ROOT_PATH)/lib
endif



## C Compiler (CC), CC Flags

ifndef CROSS
CC = g++
else
CC = $(ARM_GCC_ROOT_PATH)/bin/arm-none-linux-gnueabihf-g++
endif

CFLAGS = -g -W -I $(INCLUDE_PATH) -I $(COMMON_INCLUDE_PATH) -I $(LOCAL_INCLUDE_PATH) -I $(VSG60_INCLUDE_PATH)
LFLAGS = -L:$(VSG60_LD_PATH) -l:$(VSG60_LD_PATH)/libvsg_api.so.1


## basic signal gen
siggen: $(SOURCES) Makefile BasicSignalGen.c
	@$(CC) $(CFLAGS) $(SOURCES) BasicSignalGen.c -o ./build $(VSG60_LD_PATH)/libvsg_api.so.1


## clean build
clean:
	@rm ./build
