import asyncio
import json
import requests

from lib.api.oauth import getOauthToken

async def createInvitation(config, logger, resource="createInvitation"):

    #oauthToken = await getOauthToken(config)

    # build headers and data payload for upcoming http POST to CULedger.Identity for Onboarding.
    headers = {
            'Content-Type': 'application/json', 
            'clientId': "CentralWalletPOCKeyVault",
            'Ocp-Apim-Subscription-Key': config["ocp-apim-subscription-key"],
            'IgnorePOC': '1'
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
    #code="nMeOMariKmmEJU7AqiV0/CJjITxGM411YVW4d1lrGaBwY9nFT6TqmA=="
    #inviteEndpoint ="{}member/{}/createInvitation?code={}".format(config["endpoint"], config["memberId"], code)
    inviteEndpoint ="{}member/{}/{}".format(config["endpoint"], config["memberId"], resource)

    inviteResponse = requests.post(inviteEndpoint, data=json.dumps(invitationData), headers=headers)
    if inviteResponse.status_code == 200:
        invitationResponse = inviteResponse.json()
        return invitationResponse
    else:
        logger.info(inviteResponse)
        return None
