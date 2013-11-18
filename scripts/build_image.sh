#!/bin/bash

. ../release.conf

DL=../download
BUILD=../build
PATCH=../system-patch

echo "Creating directories"
mkdir $DL
mkdir $BUILD

if [ -f $DL/$OE_REL.tar ]; then
  echo $OE_REL.tar already downloaded
else
  echo Downloading $OE_REL.tar
  wget $URL -O $OE_REL.tar
  mv $OE_REL.tar $DL
fi

echo "Cleaning build directory"
sudo rm -rf $BUILD/$RELEASE
mkdir $BUILD/$RELEASE
cd $BUILD/$RELEASE

echo "Extracting OE_REL.tar"
tar -xvf ../$DL/$OE_REL.tar

echo "Extracting squashfs partition"
sudo unsquashfs -d system-part $OE_REL/target/SYSTEM

echo "Applying patch"
sudo cp -rf ../$PATCH/. system-part
sudo sed -i 's/update.openelec.tv\/updates.php/update.smallplayer.nl\/available_updates/' system-part/usr/share/xbmc/addons/service.openelec.settings/defaults.py
sudo sed -i 's/%s.openelec.tv\/%s/update.smallplayer.nl\/updates\/%s\/%s/' system-part/usr/share/xbmc/addons/service.openelec.settings/defaults.py

echo "Creating new squashfs partition"
sudo mksquashfs system-part SYSTEM -noI -noD -noF -noX -no-xattrs
md5sum SYSTEM > SYSTEM.md5
