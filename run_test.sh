#!/bin/bash
# Time-stamp: <2021-02-05 13:51:25>
python3 simulation_test.py
echo ===============================
git status -sb
echo ===============================
read -p "Press any key to try again... " -n1 -s
echo STARTED
./run_test.sh
