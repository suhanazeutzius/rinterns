set frequency 1575.42M
set samplerate 2.048M
rx config n=20480 format=csv file=FILE timeout=5000
rx start
rx wait
