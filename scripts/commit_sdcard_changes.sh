#!/bin/bash

if [ -z "$1" ]; then
  echo "Please execute with your drive as option"
  echo " example: ./commit_sdcard_changes.sh /dev/sdb"
  exit 1
fi

STOR_PART="${1}2"
STOR_PART_MNT="/tmp/sp_stor_part"
STOR_PART_REPO="../storage"
RSYNC="rsync -a --delete-after"

echo "Mounting storage partition from sd-card"
sudo umount $STOR_PART
sudo rm -rf $STOR_PART_MNT
sudo mkdir -p $STOR_PART_MNT
sudo mount $STOR_PART $STOR_PART_MNT

if [ ! -d $STOR_PART_MNT/.xbmc ]; then
  echo "Mount failed. Wrong device?"
  exit 1
fi

echo "Resetting and cleaning repo storage folder"
git reset --hard
git clean $STOR_PART_REPO -fxd

echo "Synchronizing storage folders from sd-card to repo"
$RSYNC $STOR_PART_MNT/.xbmc     $STOR_PART_REPO
$RSYNC $STOR_PART_MNT/tvshows   $STOR_PART_REPO
$RSYNC $STOR_PART_MNT/videos    $STOR_PART_REPO
$RSYNC $STOR_PART_MNT/music     $STOR_PART_REPO
$RSYNC $STOR_PART_MNT/pictures  $STOR_PART_REPO
$RSYNC $STOR_PART_MNT/downloads $STOR_PART_REPO

echo "Reverting changes to oe_settings.xml"
git checkout -- $STOR_PART_REPO/.xbmc/userdata/addon_data/service.openelec.settings/oe_settings.xml

echo "Unmounting and syncing"
sync
sudo umount $STOR_PART

echo "Adding changes to repository"
git add $STOR_PART_REPO
echo "Please enter a commit message:"
read MESSAGE
git commit $MESSAGE
git push
git clean $STOR_PART_REPO -fxd

echo "Done"

