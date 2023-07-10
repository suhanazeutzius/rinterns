set frequency 1575.42M
set samplerate 2.048M
set biastee off
rx config channel=1,2 n=204800 format=csv file=./sample5.csv timeout=5000
rx start
rx wait
