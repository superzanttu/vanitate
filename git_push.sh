#!/bin/bash
# Time-stamp: <2021-02-10 22:49:25>

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



#!/bin/bash
v1=$1
v2=$2
while :
do
  echo "1 = Quick commit"
  echo "2 = Commit with message"
  echo "3 = Quick commit and push"
  echo "4 = Commit with message and push"
  echo "0 = Quit"
  echo -n "Press key:"
  read -n 1 -t 15 a
  printf "\n"
  case $a in
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

    0* )
      exit 0
      ;;

    * )     echo "Try again.";;
  esac
done
