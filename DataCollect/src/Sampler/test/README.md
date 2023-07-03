# Sampler Testing

Overview of testing methods for each submodule of the Sampler program.

Use Makefile commands to compile testers for each component individually. Most follow the pattern ```make <module>``` (ex. make clock). Compiles into executable ```test``` that can be run once both devices are connected correctly.

### List of make commands:

- make channel
- make clock
- make trigger
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
6. Call channel\_disable()
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

1. Open devices
2. Initialize channels
3. Enable channels
4. Call syncstream\_init()
5. Call syncstream\_handle\_csv(), writing to a file to be checked later
6. Disable channel
7. Enable channels
7. Call syncstream\_init()
8. Call syncstream\_handle\_buffers(), and check buffers for data
9. Disable channel
10. Close devices

</br>
</br>

---

## Sampler

1. Open devices
2. Setup device and stream configurations
3. Run sampler
4. Check return value
5. Close devices
6. Check output csv file

</br>
</br>

---
