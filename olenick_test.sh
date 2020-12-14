#!/bin/bash

set -e

function checkResponse() {
    action="${1}"
    rv=${2}
    response="${3}"
    [ ${rv} -ne 0 ] && echo "${action} error: ${rv}" && exit ${rv}
    respStatus=$(echo "${response}" | grep -e '^< HTTP/1\.1 [0-9]' | sed -e 's?^< HTTP/1\.1 \([0-9][0-9][0-9]\) .*$?\1?')
    ( [ -z "${respStatus}" ] || [ ${respStatus} -lt 200 ] || [ ${respStatus} -ge 300 ] ) && echo "${action} failed with status ${respStatus}" && exit -1
}

function stripResponse() {
    response="${1}"
    echo "${response}" | grep -ve '^\([*<>] \|[{}] \[[0-9]* bytes data\]\)'
}

INPUT_JSON=$(cat <<EOF
{
    "memberId": "123456789",
    "phoneNumber": "17703299814",
    "emailAddress": "",
    "displayTextFromFI": "Let's get connected via MemberPass!",
    "credentialData": {
        "CredentialId": "UUID-GOES-HERE",
        "CredentialDescription": "TESTING",
        "Institution": "Happy Members Credit Union",
        "CredentialName": "TEST CRED",
        "MemberNumber": "--",
        "MemberSince": "NOV2016"
        }
}
EOF
)

jobId=`curl -k -s \
    -H "Content-Type: application/json" \
    -H "Prefer: respond-async" \
    -H "clientId: CentralWalletPOCKeyVault" \
    -H "Ocp-Apim-Subscription-Key: 6311bd64cdce49c08577c0c8f75d54d9" \
    -X POST \
    -d "$INPUT_JSON" \
    "https://apim-culedger-test.azure-api.net/memberpass-api/member/123456789/createInvitation" | jq -r .jobId`

#echo $jobId

#echo $inviteResponse
#
#checkResponse "Invite" ${?} "${inviteResponse}"
#jobId=$(stripResponse "${inviteResponse}" | jq -r .jobId)
echo "Invite job id: ${jobId}"
echo
active="true"
while [ "$active" == "true" ]; do
	pollResponse=`curl -k -v -s \
		-H "Content-Type: application/json" \
		-H "clientId: CentralWalletPOCKeyVault" \
		-H "Ocp-Apim-Subscription-Key: 6311bd64cdce49c08577c0c8f75d54d9" \
		"https://apim-culedger-test.azure-api.net/memberpass-api/poll/$jobId" | jq -r .active`
  	#checkResponse "Poll" ${?} "${pollResponse}"
  	active=$pollResponse #$(stripResponse "${pollResponse}" | jq -r .active)
  	echo "Polling: active=$active"
done
