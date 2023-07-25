# Sampler Testing

Overview of testing methods for each component of the Sampler program.

Use Makefile commands to compile testers for each component individually. Most follow the pattern ```make <module>``` (ex. make clock). Compiles into executable ```test``` that can be run once both devices are connected correctly.

## List of make commands:

- make channel
- make clock
- make trigger
- make trigger_single
- make trigger_multi
- make trigger_syncstream
- make syncstream
- make sampler
- make sampler\_threaded
- make lowlevel
- make all
- make clean

</br>
</br>

---

### Channel Test

1. test channel\_init()
    1. create channel config & call function
    2. check function return
    3. use getters to check parameters are set to expected values
2. test channel\_enable()
    1. call function
    2. check function return
3. test channel\_disable()
    1. call function
    2. check function return


</br>
</br>

### Clock Test

1. test clock\_init()
    1. call function
    2. check function return
    3. use getters to check clock states are set to expected values

</br>
</br>

---

### Trigger Test

1. test trigger\_init()
    1. call function
    2. check function return
    3. use getters to check trigger states are set to expected values
    4. directly read registers to check trigger states are set to expected values
2. test trigger\_fire()
    1. call function
    2. check function return
    3. use getters to check trigger states are set to expected values
3. test trigger\_deinit()
    1. call function
    2. check function return
    3. use getters to check trigger states are set to expected values

</br>
</br>

---

### Trigger Single Test

1. fires a trigger on a single device. Meant for oscilloscope debugging of a single
device.

</br>
</br>

---

### Trigger Multi Test

1. fires a trigger on master device with slave configred to recieve trigger. No stream
configured. Intended for oscilloscope debugging.

</br>
</br>

---

### Syncstream Test

1. test syncstream\_handle\_csv()
    1. call syncstream\_init()
    2. check function return
    3. call syncstream\_handle\_csv()
    4. check function return
    5. "sample.csv" should appear with collected data
2. test syncstream\_handle\_buffers()
    1. call syncstream\_init()
    2. check functionr return
    3. call syncstream\_handle\_buffers()
    4. check function return
    5. check that all buffers are appopriately filled

</br>
</br>

---

### Trigger Syncstream Test

1. Uses triggers to initiate a syncstream with one device, which is configured as
slave expecting an external trigger source (pull pin low).

</br>
</br>

---

### Trigger Syncstream Master Test

1. Uses triggers to initiate a syncstream with one device, which is configred as master.

</br>
</br>

---

### Sampler Test

1. calls sampler()
2. check function return
3. check for output csv file

</br>
</br>

---

### Sampler Threaded Test

1. calls sampler\_threaded()
2. check function return
3. check for output csv file

</br>
</br>

---

### Low Level Test

1. Calls pll\_state() and clock\_vctcxo\_state(0
2. check function return
3. prints values for inspection

</br>
</br>

---

### All Test

TODO

</br>
</br>

---
