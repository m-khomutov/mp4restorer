# mp4restorer Package

**Installation**

`pip install mp4restorer-0.0.1-py3-none-any.whl`

**Usage**

`mp4restore [-h] [-sps SPS] [-pps PPS] conf dump`

Verifies mp4 file is correct by reading 'moov' and 'mdat' atoms.
Restores the file if incorrect using video data from 'mdat' and sps/pps from record channel.
Restored file name is compiled from initial file name and '-r' suffix.
Should be used as dumping post script.


**positional arguments**
* conf        recorder configuration file
* dump        mp4 file to check


**optional arguments**
* -h, --help  show this help message and exit
* -sps params   stream SPS
* -pps params   stream PPS


**restrictions**
* files with only 'vide' handler (without 'soun' or others) can be restored
* only 'avcC' atom ('hevC' is not supported) is supported


**example**

Value of '.Recording.Dumping.post-script-path' setting

`"post-script-path" : ["/home/mkh/.local/bin/mp4restore","","/opt/netris/istream3/etc/istream3.json","{dump.path}"],`
