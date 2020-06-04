#!/bin/bash

while getopts :i: opt; do
  case "${opt}" in
    i) MEMBERID=${OPTARG}
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

if [ -z $MEMBERID ]; then
  echo "===================================================================================="
  echo "USAGE:"
  echo "       -i: Member Identifier"
  echo ""
  echo "  Please provide memberId as it is required for this procedure"
  echo "===================================================================================="
  exit
fi

AUTHENTICATE=`cd /opt/culedger-core/demo/oauth/ && ./authenticate.sh -i $MEMBERID`
echo $AUTHENTICATE
