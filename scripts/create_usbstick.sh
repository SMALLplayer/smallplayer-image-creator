#!/bin/sh

################################################################################
#      This file is part of OpenELEC - http://www.openelec.tv
#      Copyright (C) 2009-2012 Stephan Raue (stephan@openelec.tv)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with OpenELEC.tv; see the file COPYING.  If not, write to
#  the Free Software Foundation, 51 Franklin Street, Suite 500, Boston, MA 02110, USA.
#  http://www.gnu.org/copyleft/gpl.html
################################################################################

# usage:   sudo ./create_sdcard <drive>
# example: sudo ./create_sdcard /dev/sdb
# loop example: sudo ./create_sdcard /dev/loop0 ~/vSD.img

# create an empty image file for use with loop device like this:
# dd if=/dev/zero of=~/vSD.img bs=1M count=910

. ../release.conf

OE_PATH=../build/$RELEASE/$OE_REL
STORAGE=../storage

echo $OE_PATH

if [ "$(id -u)" != "0" ]; then
  clear
  echo "#########################################################"
  echo "# please execute with 'sudo' or -DANGEROUS!!!- as root  #"
  echo "# example: sudo ./create_sdcard <drive>                 #"
  echo "#########################################################"
  exit 1
fi

if [ -z "$1" ]; then
  clear
  echo "#########################################################"
  echo "# please execute with your drive as option              #"
  echo "# example: sudo ./create_sdcard /dev/sdb                #"
  echo "# or:      sudo ./create_sdcard /dev/mmcblk0            #"
  echo "# or:      sudo ./create_sdcard /dev/loop0 ~/vSD.img    #"
  echo "# to create an image file for /dev/loop0 option:        #"
  echo "#   sudo dd if=/dev/zero of=~/vSD.img bs=1M count=910   #"
  echo "#########################################################"
  exit 1
fi

DISK="$1"
if [ "$DISK" = "/dev/mmcblk0" ]; then
  PART1="${DISK}p1"
elif [ "$DISK" = "/dev/loop0" ]; then
  PART1="${DISK}p1"
  IMGFILE="$2"
  losetup $DISK $IMGFILE
else
  PART1="${DISK}1"
fi

clear
echo "#########################################################"
echo "#                                                       #"
echo "#             OpenELEC.tv USB Installer                 #"
echo "#                                                       #"
echo "#########################################################"
echo "#                                                       #"
echo "#     This will wipe any data off your chosen drive     #"
echo "# Please read the instructions and use very carefully.. #"
echo "#                                                       #"
echo "#########################################################"

# check for some required tools

  # this is needed to partion the drive
  which parted > /dev/null
  if [ "$?" = "1" ]; then
    clear
    echo "#########################################################"
    echo "#                                                       #"
    echo "# OpenELEC.tv missing tool - Installation will quit     #"
    echo "#                                                       #"
    echo "#      We can't find the required tool \"parted\"         #"
    echo "#      on your system.                                  #"
    echo "#      Please install it via your package manager.      #"
    echo "#                                                       #"
    echo "#########################################################"
    exit 1
  fi

  # this is needed to format the drive
  which mkfs.vfat > /dev/null
  if [ "$?" = "1" ]; then
    clear
    echo "#########################################################"
    echo "#                                                       #"
    echo "# OpenELEC.tv missing tool - Installation will quit     #"
    echo "#                                                       #"
    echo "#      We can't find the required tool \"mkfs.vfat\"       #"
    echo "#      on your system.                                  #"
    echo "#      Please install it via your package manager.      #"
    echo "#                                                       #"
    echo "#########################################################"
    exit 1
  fi

  # this is needed to format the drive
  which mkfs.ext4 > /dev/null
  if [ "$?" = "1" ]; then
    clear
    echo "#########################################################"
    echo "#                                                       #"
    echo "# OpenELEC.tv missing tool - Installation will quit     #"
    echo "#                                                       #"
    echo "#      We can't find the required tool \"mkfs.ext4\"       #"
    echo "#      on your system.                                  #"
    echo "#      Please install it via your package manager.      #"
    echo "#                                                       #"
    echo "#########################################################"
    exit 1
  fi

  # this is needed to tell the kernel for partition changes
  which partprobe > /dev/null
  if [ "$?" = "1" ]; then
    clear
    echo "#########################################################"
    echo "#                                                       #"
    echo "# OpenELEC.tv missing tool - Installation will quit     #"
    echo "#                                                       #"
    echo "#      We can't find the required tool \"partprobe\"       #"
    echo "#      on your system.                                  #"
    echo "#      Please install it via your package manager.      #"
    echo "#                                                       #"
    echo "#########################################################"
    exit 1
  fi

  # this is needed to tell the kernel for partition changes
  which md5sum > /dev/null
  if [ "$?" = "1" ]; then
    clear
    echo "#########################################################"
    echo "#                                                       #"
    echo "# OpenELEC.tv missing tool - Installation will quit     #"
    echo "#                                                       #"
    echo "#      We can't find the required tool \"md5sum\"         #"
    echo "#      on your system.                                  #"
    echo "#      Please install it via your package manager.      #"
    echo "#                                                       #"
    echo "#########################################################"
    exit 1
  fi

# check MD5 sums
  echo "checking MD5 sum..."

  md5sumFailed()
  {
    clear
    echo "#########################################################"
    echo "#                                                       #"
    echo "# OpenELEC.tv failed md5 check - Installation will quit #"
    echo "#                                                       #"
    echo "#      Your original download was probably corrupt.     #"
    echo "#   Please visit www.openelec.tv and get another copy   #"
    echo "#                                                       #"
    echo "#########################################################"
    exit 1
  }

  #md5sum -c $OE_PATH/target/KERNEL.md5
  #if [ "$?" = "1" ]; then
  #  md5sumFailed
  #fi

  #md5sum -c $OE_PATH/../SYSTEM.md5
  #if [ "$?" = "1" ]; then
  #  md5sumFailed
  #fi

# (TODO) umount everything (if more than one partition)
  umount ${DISK}*

# remove all partitions from the drive
  echo "writing new disklabel on $DISK (removing all partitions)..."
  parted -s "$DISK" mklabel msdos

# create a single partition
  echo "creating partitions on $DISK..."
  parted -s "$DISK" unit cyl mkpart primary ext2 -- 0 -2

# tell kernel we have a new partition table
  echo "telling kernel we have a new partition table..."
  partprobe "$DISK"

  echo "creating filesystem on $PART1..."
  mkfs.ext2 "$PART1" -L Storage

# remount loopback device
  if [ "$DISK" = "/dev/loop0" ]; then
    sync
    losetup -d $DISK
    losetup $DISK $IMGFILE -o 1048576 --sizelimit 131071488
    PART1=$DISK
  fi

  echo "mounting storage partition"
  MOUNTPOINT=/tmp/openelec_install
  rm -rf $MOUNTPOINT
  mkdir -p $MOUNTPOINT
  mount "$PART1" $MOUNTPOINT

  echo "copying data to storage partition"
  cp $OE_PATH/../SYSTEM $MOUNTPOINT
  rsync -a -f"- .git*" -f"+ *" $STORAGE/. $MOUNTPOINT

  echo "syncing disks"
  sync

  echo "unmounting partition"
  umount $MOUNTPOINT

# cleaning
  echo "cleaning tempdir..."
  rmdir $MOUNTPOINT

# unmount loopback device
  if [ "$DISK" = "/dev/loop0" ]; then
    losetup -d $DISK
  fi

echo "...installation finished"
