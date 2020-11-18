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

INVITATION=`cd /opt/culedger-core/demo/oauth/ && rm -f ../invite.json && ./invitation.sh -i $MEMBERID > ../$MEMBERID/invite.json` 
echo "Invitation created and stored in invite.json"
