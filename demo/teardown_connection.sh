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

PACKAGE=$(cat <<EOF
{
  "memberId": "$MEMBERID"
}
EOF
)

Message=`echo $PACKAGE | base64 | awk 'BEGIN{ORS="";} {print}'`
az storage message put --content=$Message --queue-name="teardown" --connection-string=$AZURE_STORAGE_CONNECTION_STRING
