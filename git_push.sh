#!/bin/bash
# Time-stamp: <2021-02-10 22:52:52>

while :
do
  echo ===============================
  echo "  1 = Quick commit"
  echo "  2 = Commit with message"
  echo "  3 = Quick commit and push"
  echo "  4 = Commit with message and push"
  echo "  5 = Show status"
  echo "  0 = Quit"
  echo -n "Select action:"
  read -n 1 -t 15 action
  printf "\n\n"
  case $action in
    1* )
      echo Quick commit
      git add .
      git commit -m "Quick and dirty!"
      ;;

    2* )
      echo Commit with message
      read -p "Message:" commitmessage
      git add .
      git commit -m $commitmessage
      ;;

    3* )
      echo Quick commit and push
      git add .
      git commit -m "Quick and dirty!"
      git push
      ;;

    4* )
      echo Commit with message and push
      read -p "Message:" commitmessage
      git add .
      git commit -m $commitmessage
      git push
      ;;

    5* )
      git status -sb
      ;;

    0* )
      exit 0
      ;;

    * )     echo "Try again.";;
  esac
  printf "\n\n"
done
