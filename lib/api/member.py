import asyncio
import json
import requests

from lib.api.oauth import getOauthToken

async def member(config, logger):

    # build headers and data payload for upcoming http POST to CULedger.Identity for Onboarding.
    headers = {
            'Content-Type': 'application/json', 
            'Ocp-Apim-Subscription-Key': config["ocp-apim-subscription-key"],
            'clientId': "CentralWalletPOCKeyVault"
            }

    memberEndpoint ="{}member/{}".format(config["endpoint"], config["memberId"])

    memberResponse = requests.get(memberEndpoint, headers=headers)
    if memberResponse.status_code == 200:
        memResponse = memberResponse.json()
        logger.info("Success from member: %s", memResponse)
        return memResponse
    else:
        logger.info(f"Error from member:{memberResponse}")
