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

/home/pi/miniconda3/envs/py36/bin/python -u /home/pi/Downloads/捉取技術指標.py > 捉取日技術指標.log &&
echo "捉取技術指標.py is done";

/home/pi/miniconda3/envs/py36/bin/python -u /home/pi/Downloads/捉取卷商買賣.py > 捉取卷商買賣.log &&
echo "捉取卷商買賣.py is done";

/home/pi/miniconda3/envs/py36/bin/python -u /home/pi/Downloads/捉取周技術指標.py > 捉取周技術指標.log &&
echo "捉取周技術指標.py is done";

/home/pi/miniconda3/envs/py36/bin/python -u /home/pi/Downloads/捉取3大法人持股.py > 捉取3大法人持股.log &&
echo "捉取3大法人持股.py is done";

/home/pi/miniconda3/envs/py36/bin/python -u /home/pi/Downloads/捉取借還卷.py > 捉取借還卷.log &&
echo "捉取借還卷.py is done";

/home/pi/miniconda3/envs/py36/bin/python -u /home/pi/Downloads/捉取融資融卷.py > 捉取融資融卷.log &&
echo "捉取融資融卷.py is done";

/home/pi/miniconda3/envs/py36/bin/python -u /home/pi/Downloads/寫入技術指標周.py > 寫入技術指標周.log &&
echo "寫入周技術指標.py is done";

/home/pi/miniconda3/envs/py36/bin/python -u /home/pi/Downloads/捉取卷商買賣.py > 捉取卷商買賣.log &&
echo "捉取卷商買賣.py is done";

/home/pi/miniconda3/envs/py36/bin/python /home/pi/Downloads/upload.py &&
echo "upload.py is done";

exit 0
