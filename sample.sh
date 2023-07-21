set biastee off
set frequency rx 1575.42M
set samplerate rx 2.046M
rx config channel=1,2 n=204600 format=csv file=/home/empire/Desktop/sample.csv timeout=5000
rx start
rx wait
