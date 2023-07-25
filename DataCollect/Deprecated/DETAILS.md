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

### Details

Initializing a trigger simply initializes the data structure that will be used in future API calls.
When the user arms a trigger, this gates all samples that would be coming through by marking their
stream bits invalid in the FPGA. Arming the trigger also sets up the expansion pin as input/output
with a pullup to 3.3V. When the user fires a trigger, the expansion pin is pulled low and the streams
in the FPGA are marked as valid, allowing them to reach the USB buffers.

### Complications/Important Notes:

<span style="color:red">

- Currently, the only trigger signal usable on the FPGA is mini-exp[1] which is pin J51-1 on the
blade xA9 (see [Schematic](/images/brf_miniexp_schematic.jpg) and [PCB](/images/brf_miniexp_pcb.jpg)
- Triggers must be disarmed prior to stoppage of sample streams (ie triggers must be
disarmed prior to enable module = false API call)
- Stream timeouts should be set to be long enough to accomodate the expected delay before
the triggers are fired (ie span the time between init & trigger fire)

</span>

### Questions:

<span style="color:blue">

- If device 1 has RX channel 0 as the master trigger, is it necessary to specify device 1's RX channel 1
as a slave, or will the channel be gated as associated with the RX channel 0?

</span>

---

</br>
</br>

## 2. Clocking

### Overview

In order to allow for triggering, we need the sample rates to align extremely precisely, this means
feeding them the same clock. This can be done with the 10MHz clock in and clock out on BladeRF 2.0 (and potentially improved by providing an external Reference In for the PLL).

### Details

The connection between the two devices is a set of CLK IN and CLK OUT ports on each device, relating to 10MHz
reference sharing. These ports are U.FL connections, which will be routed through a U.FL to SMA, then through
SMA to SMA, then back to SMA to U.FL.

### Questions:

<span style="color:blue">

- How important is clock drift in our application? Is this all handled by our post-processing correlation?
- Does the multiple connections have an impact on clock signal integrity? Can we / do we even need to measure this?

</span>

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

- Is it necessary to "clear" the buffers when having a triggered operation? For example if we used warmup sampling
as a separate operation, then wanted to do triggered sampling, will the buffers in the device be full of old data
from before the trigger was armed? If so should we somehow clear it out or merely truncate it? How do we know
where to truncate it?

</span>

---

</br>
</br>
