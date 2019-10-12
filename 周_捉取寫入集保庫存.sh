#!/bin/bash

currentDate=`date`

echo $currentDate

# current_date_time="`date "+%Y-%m-%d %H:%M:%S"`";
# echo $current_date_time;

cd /home/pi/Downloads

/home/pi/miniconda3/envs/py36/bin/python /home/pi/Downloads/捉取寫入集保庫存.py \
"20190927" "20190920" "20190912" "20191009" "20191005"

echo "執行捉取寫入集保庫存結束"

exit 0
