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

INVITATION=`cd /Users/twshelton/Workspace/CULedger/CULedger.IdentityDocs/oauth/ && ./invitation.sh -i $MEMBERID | jq -r .invitationJSON` 
PACKAGE=$(cat <<EOF
{
  "memberId": "$MEMBERID",
  "invitation": $INVITATION,
  "actions": [
    {
      "connect": {
        "respondConnectionOfferAfter": 5,
        "respondCredentialOfferAfter": 5
      }
    },
    {
      "respondAuth": {
        "respondAfter" : 5
      },
      "respondSimpleAuth": {
        "respondAfter" : 5
      }

    },
    {
      "respondProof": {
        "respondAfter" : 5
      }

    }
  ]
}
EOF
)

Message=`echo $PACKAGE | base64`
az storage message put --content=$Message --queue-name="connection" --connection-string=$AZURE_STORAGE_CONNECTION_STRING
