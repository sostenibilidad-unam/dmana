#!/bin/bash

DB=/var/www/agnes/website/db.sqlite3
BAK=~/backups

BAK_RPATH=rgh@patung.mine.nu:./agnes_bak
BAK_LPATH=~/bakhost

mkdir -p $BAK
mkdir -p $BAK_LPATH

# local copy of media files
cp -Rv /var/www/agnes/website/static $BAK/

# local copy of database
DATE=`date -I`
cp $DB  $BAK/${DATE}_db.sqlite

# mount remote site
sshfs -o nonempty $BAK_RPATH $BAK_LPATH

cd $BAK_LPATH

rsync -vaz --no-owner --no-group $BAK .

cd $BAK

sleep 5

fusermount -u $BAK_LPATH
