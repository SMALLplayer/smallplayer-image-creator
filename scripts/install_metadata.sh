#!/bin/bash

META=../metadata
MOUNT=/mnt/oe-storage

sudo mkdir -p $MOUNT

echo "Mounting storage partition"
sudo umount "$1"2
sudo mount "$1"2 $MOUNT

if [ -f $META/meta.tar ]; then
  echo "Archive found"
else
  mkdir -p $META
  echo "Archive does not exist, download it"
  exit
fi

echo "Decompressing metadata"
tar --strip-components=3 -xvf $META/meta.tar -C $MOUNT

echo "Syncing"
sync

echo "Unmounting storage"
sudo umount $MOUNT
