#!/bin/bash
# Takes in 2 arguments
# Current Deployment directory ($1) and Repository name ($2)

EXPECTED_ARGS=2

if [ $# -ne $EXPECTED_ARGS ]
then
  echo "Incorrect args. Generated tmp file"
  exit
fi

echo "Starting bootstrap."
echo "Adding repository. Assuming public key has been added."
cd /home/v1factory/gitolite-admin/conf
echo "" >> gitolite.conf
echo "repo $2" >> gitolite.conf
# TODO: change this to the user
echo "    RW+     =   www-data" >> gitolite.conf
echo "    RW+     =   vps" >> gitolite.conf
git add gitolite.conf
# TODO: change this to the user
git commit -m "Added repository $2 for vps"
git push
echo "Changing directory to /var/www/git-apps"
cd /var/www/git-apps
echo "Creating repository $2"
git clone git@staging.appcubator.com:$2
echo "Adding relevant files into $2"
cd $2
cp -r $1/webapp/ .
cp -r $1/*.py .
git add *.py webapp/
git commit -m "Bootstrap Commit."
git push origin master
echo "Success!"
exit
