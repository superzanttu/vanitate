#!/bin/bash
# Time-stamp: <2021-02-05 14:17:22>

commitmsg="Quick and dirty push!"

if [ ! $# -eq 0 ]; then
  commitmsg=${*:1}
fi

git add .
git commit -m "$commitmsg"
git push

echo ===============================
git status -sb
echo ===============================
