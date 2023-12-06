#!/bin/bash

VERSION=0.1

RedHat() {
  OUTPUT=$(needs-restarting -r 2>&1)
  case $? in
    0) printf "%s\nVersion: %s." "$OUTPUT" "$VERSION"
       exit 0
       ;;
    1) printf "%s\nVersion: %s." "$OUTPUT" "$VERSION"
       exit 2
       ;;
    *) printf "%s\nVersion: %s." "$OUTPUT" "$VERSION"
       exit 3
       ;;
  esac
}

Debian() {
  if [ -f /var/run/reboot-required ]
  then
    KERNEL=$(uname -r)
    echo "Reboot Required. Version: $VERSION.";
    echo "Current kernel: $KERNEL"
    PKG=linux-$(echo $KERNEL | cut -d- -f3)
    dpkg --status $PKG
    exit 2
  fi
  echo "No Reboot Required. Version: $VERSION.";
  exit 0
}

if [ -f /etc/redhat-release ]
then
  RedHat
elif [ -f /etc/os-release ]
then
  Debian
fi

echo "OS Type unknown. Version: $VERSION."
echo 3
