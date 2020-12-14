import asyncio
import json
import requests

from lib.api.oauth import getOauthToken

async def authenticate(config, logger, resource="authenticateSimple"):

    #oauthToken = await getOauthToken(config)

    # build headers and data payload for upcoming http POST to CULedger.Identity for Onboarding.
    headers = {
            'Content-Type': 'application/json', 
            'clientId': "CentralWalletPOCKeyVault",
            'Ocp-Apim-Subscription-Key': config["ocp-apim-subscription-key"]
            }

    #logger.info("Getting invitation with config: %s", config)

    authSimpleChallenge = {
            "messageId": "42",
            "messageQuestion": "Are you on the phone with UNIFY?",
            "messageTitle": "UNIFY Credit Union is asking you a question",
            "messageText": "We need to make sure that you are on the phone with one of our operators. We do this to protect you and your accounts at the credit union.",
            "positiveOptionText": "Yes, it is me.",
            "negativeOptionText": "No. I am NOT. That is not me.",
            "expires": "2020-01-29T19:15:17.897Z"
            }

    code="nMeOMariKmmEJU7AqiV0/CJjITxGM411YVW4d1lrGaBwY9nFT6TqmA=="
    authEndpoint ="{}member/{}/{}?code={}".format(config["endpoint"], config["memberId"], resource, code)

    authResponse = requests.put(authEndpoint, data=json.dumps(authSimpleChallenge), headers=headers)
    if authResponse.status_code == 200:
        authenticateResponse = authResponse.json()
        return authenticateResponse
