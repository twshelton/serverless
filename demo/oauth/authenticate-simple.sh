#!/bin/bash

source ./config.sh

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
  echo "  -i: Member Identifier"
  echo ""
  echo "  Please provide memberId as it is required for this procedure"
  echo "===================================================================================="
  exit
fi

input_json=$(cat <<EOF
{
    "messageId": "42",
    "messageTitle": "UNIFY Credit Union is asking you a question",
    "messageQuestion": "Hi, John",
    "messageText": "Are you talking to the UNIFY call center?",
    "positiveOptionText": "Yes, I am",
    "negativeOptionText": "No, I am not"
}
EOF
)

TOKEN=$(curl -s -X POST \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "client_id=$CLIENTID" \
        -d "grant_type=client_credentials" \
        -d "client_secret=$SECRET" \
        "https://login.microsoftonline.com/$TENANTID/oauth2/token" | jq -r .access_token)

curl -v \
  -X PUT \
  -H "Content-Type: application/json" \
  -d "$input_json" \
  -H "Authorization: Bearer $TOKEN" \
  "$ENDPOINT/member/$MEMBERID/authenticateSimple"
