# IDARM

This project is building a sqlite3 database of Cores, peripherals, registers and flags
for all ARM (and possibly other cores) microcontroller's that are supported by cmsis-svd. 

In by itself this is not a real tool but actually something for other tools to build upon.

It used to be something i build for IDA but i got frustrated with her... guess you can IDentify ARM chips with that now...
Or do stuff to/with them bits of expensive sand :tongue:...

## What do i do this this anyways ?

An exemple tool built on the IDARM database can be found here : https://github.com/Jegeva/ghidrARMloader

This is a loader module for ghidra that tags all the registers,
flags and declares registers as structures to help with reverse engineering
microcontroller firmware.

Building other tools (such as fingerprinting a piece of firmware's target with libcapstone based on the used peripherals and libcapstone) should be much easier.

## building the database 

:bell: Do not forget to clone with --recurse-submodules

:bell: start with `make` in ads2svd 

Launching adarm2.py --help

```console
./idarm2.py --help
usage: idarm2.py [-h] [-v VENDOR] [-c CHIP] [-C CORE] [-m MAX_SEGMENT_SZ] [--max-segment-sz-int MAX_SEGMENT_SZ_INT] [-d DATABASE] [-D] [-r] [-n] [-N] [-V]

makes segments for ida given a svd descripted ARM chip

optional arguments:
  -h, --help            show this help message and exit
  -v VENDOR, --vendor VENDOR
                        chip vendor, (needs a model)
  -c CHIP, --chip CHIP  chip model ,(needs a vendor)
  -C CORE, --core CORE  a specific core
  -m MAX_SEGMENT_SZ, --max-segment-sz MAX_SEGMENT_SZ
                        max segment size (fallback to db, then 0x00001000) if you need that for some reason
  --max-segment-sz-int MAX_SEGMENT_SZ_INT
                        chip model
  -d DATABASE, --database DATABASE
  -D, --dump
  -r, --rebuild-database
  -n, --no-database
  -N, --no-descriptions
  -V, --verbose
```

if you want to build the database to use in your own tool or in the ghidra loader, your are probably interested in :
```console
./idarm2.py -r -N
```

## using the database

Since i am no database expert, i went for stupid normal 3NF (uni... it does... things... to you...)

The schema can be found here : https://github.com/Jegeva/idarm/blob/master/bd.sql

## Bruh, I'm just here for the database

The resulting dbs can be found :

without the textual descriptions (~600MB): https://github.com/Jegeva/idarm-resultdb-nodescription

with the textual descriptions    (~900MB): https://github.com/Jegeva/idarm-resultdb-withdescription


The datasources that are used are :
- cmsis-svd (https://github.com/Jegeva/cmsis-svd) for parsing the svd xml files with the vendor information
- ads2svd (https://github.com/Jegeva/ads2svd/) : cleans ARM devellopment studio companion xml files and transforms them to svd for the core peripherals information

This is released under Apache license : https://www.apache.org/licenses/LICENSE-2.0


