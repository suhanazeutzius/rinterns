# Phase Adjustment Python

## Overview

1. Read a csv to complex lists for each channel
2. Pass to phasecalculator function & get 3 phase deltas
3. Pass lists & phase deltas to phaseimposer function & get new lists
4. Write lists to csv

## Implementation of Phase Adjustment


### "Behind the Scenes Functions"
- readcsv() -- handles csv to complex list conversion (with automatic channel number adjustment)
- phasecalculate() -- handles phase calculation between two signals of known center frequency and sample rate
- phaseimpose() -- imposes a set of phase differences on a set of signal samples

### User Functions
- phasecalculator -- calculates a set of phases & stores of a file with a known center frequency and sample rate
- phaseadjust -- adjusts a file of data from the stored phases and re-writes to the same file
