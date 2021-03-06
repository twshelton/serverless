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

INVITATION=`cat $MEMBERID/invite.json | jq -r .invitationJSON`
JOBID=`cat $MEMBERID/invite.json | jq -r .jobId`

PACKAGE=$(cat <<EOF
{
  "memberId": "$MEMBERID",
  "invitation": $INVITATION,
  "jobId": "$JOBID"
}
EOF
)
#need to encode the message and then remove the line breaks
Message=`echo $PACKAGE | base64 | awk 'BEGIN{ORS="";} {print}'`
az storage message put --queue-name="connection-$MEMBERID" --connection-string=$AZURE_STORAGE_CONNECTION_STRING --content=$Message 
