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
  echo "  Please provide a memberId as it is required for this procedure"
  echo "===================================================================================="
  exit
fi

TOKEN=$(curl -s -X POST \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "client_id=$CLIENTID" \
        -d "grant_type=client_credentials" \
        -d "client_secret=$SECRET" \
        "https://login.microsoftonline.com/$TENANTID/oauth2/token" | jq -r .access_token)

curl -v \
  -d '' \
  -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  "$ENDPOINT/member/$MEMBERID/authenticate"
