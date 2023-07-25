# Front End Data Collection

Communication, configuration, and data collection with the BladeRF for
4-element antenna array for direction finding of a GPS satellite using
interferometry.

</br>
</br>

---

## Program Components:

The Sampler Program is the main program for front end data collection. It initializes
the blade connection, the blade parameters, and the stream configurations. The Sampler
program is further broken down into the following:

1. Channel
2. Clock
3. Trigger
4. Syncstream
5. Sampler
6. PLL

Each are given subsections in this document. Functions are listed without parameter
or return types. Note that testing of these functions is done within src/Sampler/test.
That directory has its own README describing its components.

</br>
</br>

---

## 1. Channel

The channel component configures channel properties, including frequency, bandwidth,
gain modes and gain values, sample rate, and biastee.

### Channel Functions

- channel\_init()
- channel\_enable()
- channel\_disable()

### Channel Datatypes

- struct channel\_config

</br>
</br>

---

## 2. Clock

The clock component configures the clock sharing interface for master and slave
devices. It additionally allows for viewing of the VCTCXO state.

### Clock Functions

- clock\_init()
- clock\_vctcxo\_state()

</br>
</br>

---

## 3. Trigger

The trigger component configures master and slave triggers, which will allow for
simultaneous sampling stream start between two bladeRF devices.

### Trigger Functions

- trigger\_init()
- trigger\_deinit()
- trigger\_fire()
- trigger\_fire\_task()

### Trigger Datatypes

- struct trigger\_task\_arg

</br>
</br>

---

## 4. Syncstream

Syncstream configures, executes, and handles a USB stream between the bladeRF
and the controlling device.

### Syncstream Functions

- syncstream\_init()
- syncstream\_init\_task()
- syncstream\_handle\_csv()
- syncstream\_handle\_buffers()
- syncstream\_free\_buffers()
- \_syncstream\_init\_config()
- \_syncstream\_init\_buffers()

### Syncstream Datatypes

- struct stream\_config
- struct stream\_task\_arg

</br>
</br>

---

## 5. Sampler

Sampler component gathers all of the other components together to take samples
for a 4-element, 2-bladeRF system which shares clock references and executes
on trigger with input channel and stream configurations.

### Sampler Functions

- sampler()
- sampler\_threaded()
- \_sampler\_init()

</br>
</br>

---

## 6. PLL

PLL program prints states of the AD400F PLL chip for debugging.

### PLL Functions

- pll\_state()
