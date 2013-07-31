#!/bin/bash
# Takes in 2 arguments
# Bare Repository and Current Deployment directory

EXPECTED_ARGS = 2

if [ $# -ne $EXPECTED_ARGS ]
then
  echo "Incorrect args. Generated tmp file"
  touch /tmp/incorrect_args.txt
  exit
fi

echo "Starting bootstrap."
cd /var/www/apps/$2
echo "Changing directory to git-apps/$1"
cd /var/www/git-apps/
mkdir $1
cd $1
echo "Initializing bare git repository."
git init --bare
cd ..
echo "Changing directory to $2"
cd /var/www/apps/$2
git init
git add *.py webapp/
git commit -am "Bootstrap Commit."
git remote add appcubator git@staging.appcubator.com:/var/www/git-apps/$1/
echo "Success!"
