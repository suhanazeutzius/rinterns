# Sampler Testing

Overview of testing methods for each submodule of the Sampler program.

Use Makefile commands to compile testers for each component individually. Most follow the pattern ```make <module>``` (ex. make clock). Compiles into executable ```test``` that can be run once both devices are connected correctly.

### List of make commands:

- make channel
- make clock
- make trigger_oscope
- make trigger_syncstream
- make syncstream
- make sampler
- make all
- make clean


</br>
</br>

---

## Channel

1. Open devices
2. Call channel\_init() with regular config values
3. Use API getters to check gpio config matches channel config
4. Call channel\_enable()
5. Check status of front end modules to ensure they are enabled
6. Call channel\_deinit()
7. Check status of front end modules to ensure they are disabled
8. Close devices

</br>
</br>

---

## Clock

1. Open devices
2. Call clock\_init()
3. Use API getters to check gpio config matches clock config
4. Close device

</br>
</br>

---

## Trigger

**Note: trigger has two builds, one for testing miniexp trigger signal with an
oscilloscope, one for testing using a syncstream**

</br>

1. Open devices
2. Call trigger\_init()
3. Use API triggers state fn to check triggers match config
4. Call trigger\_fire() w/ mini expansion disconnected
5. Check with oscilloscope that the mini expansion changed state on master
6. Configure a Rx stream on slave & master
7. Call trigger\_fire() w/ mini expansion connected
8. Check that both streams are recieved
9. Call trigger\_deinit()
10. Use API triggers state fn to check triggers match disabled state
11. Close devices

</br>
</br>

---

## Syncstream

COMING SOON

</br>
</br>

---

## Sampler

COMING SOON

</br>
</br>

---
