import asyncio
import json
import requests
import logging

from lib.api.oauth import getOauthToken

async def createInvitation(config):

    logger = logging.getLogger(__name__)
    #oauthToken = await getOauthToken(config)

    # build headers and data payload for upcoming http POST to CULedger.Identity for Onboarding.
    headers = {
            'Content-Type': 'application/json', 
            'clientId': "CentralWalletPOCKeyVault"
            }

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
    code="nMeOMariKmmEJU7AqiV0/CJjITxGM411YVW4d1lrGaBwY9nFT6TqmA=="
    #inviteEndpoint ="{}member/{}/createInvitation?code={}".format(config["endpoint"], config["memberId"], code)
    inviteEndpoint ="{}member/{}/pocendpoint?code={}".format(config["endpoint"], config["memberId"], code)

    inviteResponse = requests.post(inviteEndpoint, data=json.dumps(invitationData), headers=headers)
    if inviteResponse.status_code == 200:
        invitationResponse = inviteResponse.json()
        return invitationResponse
    else:
        logging.info(inviteResponse)
        return None
