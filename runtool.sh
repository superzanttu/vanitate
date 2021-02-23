#!/bin/bash
# Time-stamp: <2021-02-22 23:37:12>

while :
do
  ct=$(date +"%T")

  echo ===============================
  echo "  r - Run start.sh"
  echo "  l - Quick local commit"
  echo "  q - Quick local commit and push"
  echo "  p - Local commit with message and push"
  echo "  u - Push"
  echo "  s - Status"
  echo "  0 - Quit"
  echo -------------------------------
  echo "Status at $ct"
  git status -sb
  echo -------------------------------
  echo -n "Select action:"
  read -n 1 action
  printf "\n\n"
  case $action in

    r* )
      echo === Run start.sh
      git add -v .

      git commit -m "Run"
      time ./start.sh
      ;;

    l* )
      echo === Quick local commit
      git add .
      git commit -m "Quick and dirty!"
      ;;

    q* )
      echo === Quick local commit and push
      git add .
      git commit -m "Quick and dirty!"
      git push
      ;;

    p* )
      echo === Local commit with message and push
      read -p "Message:" message
      git add .
      git commit -m "$message"
      git push
      ;;

    u* )
      echo === Push
      git push
      ;;

    s* )
      echo === Status
      git status -sb
      ;;

    0* )
      exit 0
      ;;

    * )
      git status -sb
      ;;
  esac
  printf "\n"
done
