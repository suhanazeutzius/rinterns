# Front End Data Collection Program

This program calibrates and collects data in a configurable manner

</br>
</br>

## Program Components:

The following 7 components are the main pieces of the front end data collection
process, and are explained in further detail below.

1. [Warmup Sampler](##1.-warmup-sampler)
2. [Tone Generator](##2.-tone-generator)
3. [Sampler](##3.-sampler)
4. [Delta Phase Calculator](##4.-delta-phase-calculator)
5. [Delta Phase Imposer](##5.-delta-phase-imposer)

---

</br>
</br>

## 1. Warmup Sampler

### Program Overview

The purpose of the warmup sampler is to collect and trash samples for some period of time
on device startup in order to allow for the channel physical characteristics to reach a
(at least quasi)-steady state. Things such as temperature, resistance, etc, cause the samples to
change drastically from cold start to sample collection, so the initial results of sampling should
be disregarded. The warmup sampler and the regular sample vary only in how they configure and
recieve streams.

### Program Outline

SEE SAMPLER PROGRAM BELOW

### Complications and Future Considerations

<span style="color:red">

</span>

---

</br>
</br>

## 2. Tone Generator

COMING SOON

---

</br>
</br>

## 3. Sampler

### Program Overview

The sampler is the main data collection component of the front end data collection
collection. The sampler gathers a small (256-512 byte) metadata sample followed by a
larger and configurable non-metadata IQ sample.

### Program Outline

1. Open Devices?
2. Initialize clocks
3. Initialize channels
4. Enable modules
5. Initialize triggers
6. Initialize streams
7. Fire triggers
8. Handle streams
9. Disable triggers
10. Disable modules
11. Close devices?

### Complications and Future Considerations

<span style="color:red">

- Do we need/want to close the device every time?
- Do we need to disable & re-enable modules every time we start a new stream?
- Do configurations change when we are "not looking"? (Ex. gain, bandwidth, freq, etc...)

</span>

---

</br>
</br>

## 4. Delta Phase Calculator

## Program Overview

The delta phase calculator takes two channels and compares the phsae difference between them. The phase shift is calculated from a reception of a known, pure tone (see Tone generator). The phase shift is calculated relative to one of the 4 channels, and is done individually for each of the 3 other channels. This calculated delta phase is stored to be used for the delta phase imposer input.

### Program Outline

1. Collect data from sampler program
2. Calculate sum vector (Ch0 + Ch1) for two components, one of which is the base reference (Ch0)
3. Calculate the difference vector (Ch0 + Ch1) in the same way
4. Average the sum and difference vectors.
5. Calculate the ratio of difference average to sum average (R)
6. Phase is 2arctan(-Im{R})
7. Store phase
8. Repeat steps 2-7 twice, replacing Ch1 with Ch2, and then with Ch3

### Complications and Future Considerations

<span style="color:red">

- Will this method work? The original calculation was based on geometry of incoming plane waves, however this will not be the case for all of our signals. Step 6 is especially suspicious.
- What other methods could we use? Correlation?

</span>

---

</br>
</br>

## 5. Delta Phase Imposer

## Program Overview

The delta phase imposer takes the delta phase calculated for each channel and imposes it on
every data file output by the sampler according to channel. The phase shift is simply
a complex exponential multiplication.

## Program Outline

1. Open CSV file & delta phase (file/data?)
2. Parse CSV file into integer arrays
3. Conver int arrays to complex
4. Apply complex exponential multiplication to all channels independently
5. Convert back to int arrays
6. Write back to CSV

## Complications and Future Considerations

<span style="color:red">

- How to best share the delta phase information?

</span>

---

</br>
</br>
