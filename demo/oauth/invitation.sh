#!/bin/bash

source ./config.sh

set -e

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

INPUT_JSON=$(cat <<EOF
{
    "memberId": "$MEMBERID",
    "phoneNumber": "$PHONE",
    "emailAddress": "$EMAIL",
    "displayTextFromFI": "Let's get connected via MyCUID!",
    "credentialData": {
        "CredentialId": "UUID-GOES-HERE",
        "CredentialDescription": "TESTING",
        "Institution": "CULedger Credit Union",
        "CredentialName": "TEST CRED",
        "MemberNumber": "$MEMBERID",
        "MemberSince": "NOV2016"
    }
}
EOF
)

TOKEN=$(curl -s -X POST \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "client_id=$CLIENTID" \
        -d "grant_type=client_credentials" \
        -d "client_secret=$SECRET" \
        "https://login.microsoftonline.com/$TENANTID/oauth2/token" | jq -r .access_token)

curl -v -k \
  -H "Content-Type: application/json" \
  -H "Ocp-Apim-Subscription-Key: $SUBSCRIPTIONKEY" \
  -H "clientId: CentralWalletPOCKeyVault" \
  -H "Authorization: Bearer $TOKEN" \
  -X POST \
  -d "$INPUT_JSON" \
  "$ENDPOINT/member/$MEMBERID/createInvitation?code=$CODE"
