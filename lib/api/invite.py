import asyncio
import json
import requests
import logging

from lib.api.oauth import getOauthToken

async def createInvitation(config):

    logger = logging.getLogger(__name__)
    oauthToken = await getOauthToken(config)

    # build headers and data payload for upcoming http POST to CULedger.Identity for Onboarding.
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + oauthToken}

    #logger.info("Getting invitation with config: %s", config)

    invitationData = {
        "memberId": config["memberId"],
        "phoneNumber": "",
        "emailAddress": "",
        "displayTextFromFI": "Let's get connected via MyCUID!",
        "credentialData": {
            "CredentialId": "UUID-GOES-HERE",
            "CredentialDescription": "TESTING",
            "Institution": "CULedger Credit Union",
            "CredentialName": "TEST CRED",
            "MemberNumber": config["memberId"],
            "MemberSince": "NOV2016"
        }
    }

    inviteEndpoint ="{}member/{}/createInvitation".format(config["endpoint"], config["memberId"])

    inviteResponse = requests.post(inviteEndpoint, data=json.dumps(invitationData), headers=headers)
    if inviteResponse.status_code == 200:
        invitationResponse = inviteResponse.json()
        return invitationResponse['invitationJSON']
