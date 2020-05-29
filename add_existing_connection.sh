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
  "invitation": {},
  "actions": [
    {
      "connect": {
        "respondConnectionOfferAfter": 10,
        "respondCredentialOfferAfter": 10
      }
    },
    {
      "respondAuth": {
        "respondAfter" : 100
      }
    },
    {
      "respondSimpleAuth": {
        "respondAfter" : 100
      }

    },
    {
      "respondProof": {
        "respondAfter" : 100
      }

    }
  ]
}
EOF
)

Message=`echo $PACKAGE | base64`
az storage message put --content=$Message --queue-name="connection" --connection-string=$AZURE_STORAGE_CONNECTION_STRING
