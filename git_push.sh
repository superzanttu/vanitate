#!/bin/bash

commitmsg="Quick and dirty push!"

if [ ! $# -eq 0 ]; then
  commitmsg=${*:1}
fi

git add .
git commit -m "$commitmsg"
git push
