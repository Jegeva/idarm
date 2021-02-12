This project is building a database of ARM (and possibly other cores) microcontroller :

Cores, peripherals, registers and flags

In by itself this is not a real tool but actually something for other tools to build upon.

An exemple tool can be found here :

This is a loader module for ghidra that tags all the registers,
flags and declares registers as structures t ohelp with reverse engineering
microcontroller firmware.

Building other tools (such as fingerprinting a piece of firmware's target with
libcapstone based on the used peripherals) should be much easier.rm libcapstone

![Warning](https://upload.wikimedia.org/wikipedia/commons/c/c3/GHS-pictogram-exclam.svg)
Do not forget to clone with --recurse-submodules

The datasources that are used are :
- cmsis-svd (for parsing the svd xml files) for the microcontroller vendor information
- ads2svd : cleans ARM devellopment studio companion xml files and transforms them to svd for the core peripherals information

This is released under Apache license : https://www.apache.org/licenses/LICENSE-2.0