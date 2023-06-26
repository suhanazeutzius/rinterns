## Paths / Sources

SOURCE_PATH = ../
INCLUDE_PATH = ../

SOURCES = $(SOURCE_PATH)/channel.c $(SOURCE_PATH)/clock.c $(SOURCE_PATH)/sampler.c $(SOURCE_PATH)/syncstream.c $(SOURCE_PATH)/trigger.c


## C Compiler / Flags
CC = gcc -g -W -I $(INCLUDE_PATH) -l:libbladeRF.so -l:libbladeRF.so.2


## test channel
channel: $(SOURCES) Makefile test_channel.c
	@$(CC) $(SOURCES) test_channel.c -o ./test

## test clock
clock: $(SOURCES) Makefile test_clock.c
	@$(CC) $(SOURCES) test_clock.c -o ./test

## test trigger
trigger: $(SOURCES) Makefile test_trigger.c
	@$(CC) $(SOURCES) test_trigger.c -o ./test

## test syncstream
syncstream: $(SOURCES) Makefile test_syncstream.c
	@$(CC) $(SOURCES) test_syncstream.c -o ./test

## test all
all: $(SOURCES) Makefile test_all.c
	@$(CC) $(SOURCES) test_all.c -o ./test


## clean build
clean:
	@rm ./test
