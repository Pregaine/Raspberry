#!/bin/bash
# Program:
#       This program shows "Hello World!" in your screen.
# History:
# 2019/06/20	VBird	First release
# PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin

# export PATH

current_date_time="`date "+%Y-%m-%d %H:%M:%S"`";

echo $current_date_time;

cd /home/pi/Downloads/

/home/pi/miniconda3/envs/py36/bin/python -u /home/pi/Downloads/寫入技術指標周.py > 寫入技術指標周.log &

echo "python -u 寫入技術指標周.py > 寫入技術指標周.log & \a \n"

exit 0