# pymp4restorer Package

**Installation**

`pip install mp4restorer-0.0.1-py3-none-any.whl`

**Usage**

`mp4restore [-h] [-channel CHANNEL] [-sps SPS] [-pps PPS] invalid restored`

Takes sps/pps from record channel. Searches 'mdat' atom in invalid file.
Compiles required atoms of mp4 structure. Saves the result in restored file.


**positional arguments**
* invalid           file with 'mdat' atom
* restored          resulted mp4 file

**optional arguments**
* -h, --help        show this help message and exit
* -channel CHANNEL  invalidly dumped channel
* -sps SPS          stream SPS
* -pps PPS          stream PPS


**restrictions**
* files with only 'vide' handler (without 'soun' or others) can be restored
* only 'avcC' atom ('hevC' is not supported) is supported


**example**

mp4restore -channel /opt/netris/istream3/storage/rec/toystory/ ~/mp4/toystory\_blv.mp4 restored.mp4
