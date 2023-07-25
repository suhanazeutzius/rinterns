# Phase Testing

Overview of testing methdos for each submodule of the Phase program.

Use Makefile commands to compile tester for each component individually. Most follow the pattern ```make <module>```
(ex. make imposer). Compiles into executable ```test``` that can be run without device connection.

### List of make commands:

- make calculator
- make imposer

</br>
</br>

---

## Calculator

1. Generate a known wave & same wave w/ phase shifts
2. Pass wave & shifted waves to phasecalculator
3. Check calculated phase shifts against true shifts

</br>
</br>

---

## Imposer

1. Generate known wave & same wave w/ phase shifts
2. Calculate phase shifts w/ phasecalculator
3. Pass phase shifts & waves to phaseimposer
4. Calculate phase shifts w/ phasecalculator
5. Check all phase shifts (should be about 0)

</br>
</br>

---
