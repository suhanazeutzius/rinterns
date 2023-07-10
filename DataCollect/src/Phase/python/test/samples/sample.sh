set biastee off
set frequency 1575.42M
set samplerate 20.048M
set clock_sel onboard
set clock_out on
rx config channel=1,2 n=204800 format=csv file=./bpsk_sample.csv timeout=10000
rx start
rx wait
