# Details on Front End Data Collection Ideas

</br>
</br>

## Table of Contents

1. [Triggers](#1.-triggers)
2. [Clocking](#2.-clocking)
3. [Streaming](#3.-recieve-streaming)

---

</br>
</br>

## 1. Triggers

### Overview

Triggers allow for device Rx and Tx operations to be triggered on an electrical event. With
multiple devices that run on the same sample rate, these should achieve synchronization within
**+/- 1 sample**. 

### Complications/Important Notes:

<span style="color:red">

- Currently, the only trigger signal usable on the FPGA is mini-exp[1] which is pin J51-1 on the
blade xA9 (see [Schematic](/images/brf_miniexp_schematic.jpg) and [PCB](/images/brf_miniexp_pcb.jpg)
- Trigger API functions must be used prior to streaming
- Triggers must be disarmed prior to stoppage of sample streams (ie triggers must be
disarmed prior to enable module = false API call)
- Stream timeouts should be set to be long enough to accomodate the expected delay before
the triggers are fired (ie span the time between init & trigger fire)

</span>

### Questions:

<span style="color:blue">

- How can you initialize a trigger for multiple channels on one device? Trigger-init requires you
to specify a channel, do you need to set up the other channel as a slave? if so, which signal
do you pick?
- How does the blade handle a triggered sample that cannot be received by the USB line until later?
- Related to above, how does "handle-rx-operations" function in example-trigger.c file work?

</span>

---

</br>
</br>

## 2. Clocking

### Overview

In order to allow for triggering, we need the sample rates to align extremely precisely, this means
feeding them the same clock. This can be done with the SMB port API.

---

</br>
</br>

## 3. Recieve Streaming

### Overview

The synchronous streaming API provices functions to keep thread stream reception of data via
libusb from the bladeRF's. Samples will not be available to recieve via sync-rx until a block of "buffer size" has been filled by the blade. There can be more than one buffer, so that while data is being transfered more samples can be filling buffer slots. The number of transfers that can be "in-flight" at one time indicates how many buffers can be "simultaneously" transferring out of the device.

### Complications/Important Notes:

<span style="color:red">

- buffer size is size of buffers in units of samples (must be multiples of 1024); smaller values help
to minimize transfer latency, but require the user to rapidly process the buffers (8192-16384 is recommended for non-latency sensitive applications)
- number of buffers defines how many samples buffers are allocated, meaning that more buffers ensures
that samples can continue to flow into the buffers without being overrun, but also increasing the number
of buffers increases the chances of latency issues
- number of transfers defines how many buffers may be in flight at any given time. This should be less
than or equal to half of the number of buffers

</span>

### Questions:

<span style="color:blue">

</span>

---

</br>
</br>
