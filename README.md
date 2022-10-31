# mp4restorer Package

**Installation**

`pip install mp4restorer-0.0.1-py3-none-any.whl`

**Usage**

`mp4restore [-h] [-sps SPS] [-pps PPS] [-sprop SPROP] [-conf CONF] dump`

Verifies mp4 file is correct by reading 'moov' and 'mdat' atoms.
Restores the file if incorrect using video data from 'mdat' and sps/pps from record channel or arguments.
Restored file name is compiled from initial file name and '-r' suffix.
Can be used as dumping post script.


**positional arguments**
* dump        mp4 file to check


**optional arguments**
* -h, --help  show this help message and exit
* -sps params   stream SPS
* -pps params   stream PPS
* -sprop SPROP  current-sprop-string
* -conf CONF  recorder configuration file


**restrictions**
* files with only 'vide' handler (without 'soun' or others) can be restored
* only 'avcC' atom ('hevC' is not supported) is supported


**example**

`mp4restore b55d84be-676c-46cd-b37a-c738524b3c11.mp4 -sps 78118.sps -pps 78118.pps`

**post dump script example**

Value of '.Recording.Dumping.post-script-path' setting

`"post-script-path" : ["/home/mkh/.local/bin/mp4restore","","-conf","/opt/netris/istream3/etc/istream3.json","{dump.path}"],`
