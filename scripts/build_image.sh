#!/bin/bash

if [ "$(id -u)" != "0" ]; then
  echo "Please execute with sudo or as root"
  exit 1
fi

. ../release.conf

DL=../download
BUILD=../build
PATCH=../system-patch

echo "Creating directories"
mkdir -p $DL
mkdir -p $BUILD

if [ -f $DL/$OE_REL.tar ]; then
  echo $OE_REL.tar already downloaded
else
  echo Downloading $OE_REL.tar
  wget $URL -O $OE_REL.tar
  mv $OE_REL.tar $DL
fi

echo "Cleaning build directory"
rm -rf $BUILD/$RELEASE
mkdir $BUILD/$RELEASE
cd $BUILD/$RELEASE

echo "Extracting OE_REL.tar"
tar -xvf ../$DL/$OE_REL.tar

echo "Extracting squashfs partition"
unsquashfs -d system-part $OE_REL/target/SYSTEM

echo "Applying patch"
cp -rf ../$PATCH/. system-part
sed -i 's/update.openelec.tv\/updates.php/update.smallplayer.nl\/available_updates/' system-part/usr/share/xbmc/addons/service.openelec.settings/defaults.py
sed -i 's/%s.openelec.tv\/%s/update.smallplayer.nl\/updates\/%s\/%s/' system-part/usr/share/xbmc/addons/service.openelec.settings/defaults.py

echo "Creating new squashfs partition"
mksquashfs system-part SYSTEM -noI -noD -noF -noX -no-xattrs
md5sum SYSTEM > SYSTEM.md5
