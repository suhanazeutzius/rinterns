#!/bin/bash

# get filename
if [ -z "$1" ]
then
    echo "Missing required argument FILENAME";
    echo "Usage: bash ./datacollect.sh <FILENAME>";
    exit -1;
fi
FILENAME=$1

# create working directory & check for clean command
if [ ! -d "./.datacollect" ]
then
    mkdir .datacollect;
fi

SCRIPT_FILE=./.datacollect/brf_script.sh
LOG_FILE=./.datacollect/brf_log.log

# create new brf script file
if [ -f $SCRIPT_FILE ]
then
    rm $SCRIPT_FILE;
fi
touch $SCRIPT_FILE;

# generate script
echo 'set frequency rx 1575.42M' >> $SCRIPT_FILE;
echo 'set samplerate rx 2.046M' >> $SCRIPT_FILE;
echo 'set biastee off' >> $SCRIPT_FILE;
echo 'rx config channel=1,2 n=204600 timeout=5000 format=csv file='$FILENAME >> $SCRIPT_FILE;
echo 'rx start' >> $SCRIPT_FILE;
echo 'rx wait' >> $SCRIPT_FILE;

# execute script
bladeRF-cli --script $SCRIPT_FILE;
ret=$?

# remove script file
if [ -f $SCRIPT_FILE ]
then
    rm $SCRIPT_FILE;
fi

# if script returns error, log and exit
if [ "$ret" != "0" ]
then
    # generate log file
    if [ ! -f $LOG_FILE ]
    then
        touch $LOG_FILE;
    fi

    # write log file
    get_time=`date`
    echo '['${get_time}']: BRF Status '$ret >> $LOG_FILE;

    # exit status
    exit $ret
fi

exit 0;
