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
  "memberId": "$MEMBERID",
  "actions": [
    {
      "connect": {
        "respondConnectionOfferAfter": 10,
        "respondCredentialOfferAfter": 10
      }
    },
    {
      "respondAuth": {
        "respondAfter" : 10
      }
    },
    {
      "respondSimpleAuth": {
        "respondAfter" : 10
      }

    },
    {
      "respondProof": {
        "respondAfter" : 10
      }

    }
  ]
}
EOF
)

Message=`echo $PACKAGE | base64 | awk 'BEGIN{ORS="";} {print}'`
az storage message put --content=$Message --queue-name="initialize" --connection-string=$AZURE_STORAGE_CONNECTION_STRING
