set frequency rx 424.42M
set samplerate rx 8.184M
set biastee off
rx config channel=1,2 n=818400 format=csv file=/home/empire/Desktop/sample.csv timeout=5000
rx start
rx wait
