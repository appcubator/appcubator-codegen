#!/bin/bash
# Takes in 2 arguments
# Bare Repository and Current Deployment directory

echo "Starting bootstrap."
cd /var/www/apps/$1
echo "Changing directory to git-apps/$1"
cd ../../../git-apps/
mkdir $1
cd $1
echo "Initializing bare git repository."
#git init --bare
echo "Changing directory to $2"
cd ../../apps/
cd $2
#git init
#git add *.py webapp/
#git commit -am "Bootstrap Commit."
#git remote add appcubator v1factory@staging.appcubator.com:/var/www/git-apps/$2/
#git push appcubator master
echo "Pushed code to bare git repository."
echo "Success!"
