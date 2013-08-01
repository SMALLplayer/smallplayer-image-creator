#!/bin/bash

. ../release.conf

DL=../download
BUILD=../build
PATCH=../patch

echo "Creating directories"
mkdir $DL
mkdir $BUILD

if [ -f $DL/$OE_REL.tar ]; then
  echo $OE_REL.tar already downloaded
else
  echo Downloading $OE_REL.tar
  wget $URL -O $OE_REL.tar
  mv $FILE $DL
fi

echo "Cleaning build directory"
sudo rm -rf $BUILD/$RELEASE
mkdir $BUILD/$RELEASE
cd $BUILD/$RELEASE

echo "Extracting OE_REL.tar"
tar -xvf ../$DL/$OE_REL.tar

echo "Extracting squashfs partition"
sudo unsquashfs -d system  $OE_REL/target/SYSTEM

echo "Applying patch"
sudo cp -rf ../$PATCH/. system

echo "Creating new squashfs partition"
sudo mksquashfs system SYSTEM -noI -noD -noF -noX -no-xattrs
md5sum SYSTEM > SYSTEM.md5
