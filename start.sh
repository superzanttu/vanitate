#!/bin/bash
# Time-stamp: <2021-02-23 20:30:36>
FGWHITE=`echo "33[1;37m"`
echo "${FGWHITE}"
echo Running...
python3 simulation_test.py
NORMAL=`echo "33[m"`
echo "${NORMAL}"
