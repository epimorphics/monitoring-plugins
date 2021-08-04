#!/usr/bin/env bash
# Nagios Exit Codes
OK=0
WARNING=1
CRITICAL=2
UNKNOWN=3

SERVICE=$1
PROG=$(basename $0)

if [ -z "$SERVICE" ] 
then
  echo "Usage:"
  echo "	$PROG service"
  echo 
  exit $UNKNOWN
fi

if [ -x /bin/systemctl ] || [ -x /usr/bin/systemctl ]
then

  ACTIVE=$(systemctl is-active $SERVICE)

  if [ -z "$ACTIVE" ] || [ "$ACTIVE" == "unknown" ] 
  then
    echo "$SERVICE: unknown service"
    exit $UNKNOWN
  else
    systemctl status -n0 $SERVICE
    [ "$ACTIVE" == "active" ] && exit $OK
  fi 
  exit $CRITICAL

else

  service $SERVICE status
  case $? in 
    0)
      exit $OK;;
    1) # Unknown service
      exit $UNKNOWN;;
    *)
      exit $CRITICAL;;
  esac

fi
