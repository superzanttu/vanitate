#!/bin/bash
# Time-stamp: <2021-02-10 23:05:03>

while :
do
  ct=$(date +"%T")

  echo ===============================
  echo "  1 = Quick commit 2 = Commit with message"
  echo "  3 = Push         4 = Quick commit and push 5 = Commit with message and push"
  echo "  9 = Show status  0 = Quit"
  echo -------------------------------
  echo Status at $ct
  git status -sb
  echo -------------------------------
  echo -n "Select action:"
  read -n 1 -t 600 action
  printf "\n\n"
  case $action in
    1* )
      echo === Quick commit
      git add .
      git commit -m "Quick and dirty!"
      ;;

    2* )
      echo === Commit with message
      read -p "Message:" commitmessage
      git add .
      git commit -m "$commitmessage"
      ;;

    3* )
      echo === Push
      git push
      ;;

    4* )
      echo === Quick commit and push
      git add .
      git commit -m "Quick and dirty!"
      git push
      ;;

    5* )
      echo === Commit with message and push
      read -p "Message:" commitmessage
      git add .
      git commit -m "$commitmessage"
      git push
      ;;

    9* )
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
