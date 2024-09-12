#!/usr/bin/env bash
# Nagios Exit Codes
OK=0
WARNING=1
CRITICAL=2
UNKNOWN=3

NAME=$1
PROG=$(basename $0)

check () 
{
  STATUS=$(docker container inspect $NAME 2> /dev/null | jq -r .[0].State.Status)
  
  case $STATUS in 
    running)
       docker container stats --no-stream $NAME 2>&1
       exit $OK;;
    *) [ "$STATUS" == "null" ] && echo "Container $NAME not running" || echo "Container $NAME $STATUS"
       exit $CRITICAL;;
  esac
}


if [ -z "$NAME" ] 
then
  echo "Usage:"
  echo "	$PROG container"
  echo 
  exit $UNKNOWN
fi

if [ -x /bin/systemctl ] || [ -x /usr/bin/systemctl ]
then

  ACTIVE=$(systemctl is-active docker)

  if [ -z "$ACTIVE" ] || [ "$ACTIVE" == "unknown" ] 
  then
    echo "docker: unknown service"
    exit $UNKNOWN
  else
    [ "$ACTIVE" == "active" ] && check
  fi 
  exit $CRITICAL

else

  service docker status
  case $? in 
    0)
      check;;
    1) # Unknown service
      exit $UNKNOWN;;
    *)
      exit $CRITICAL;;
  esac

fi
