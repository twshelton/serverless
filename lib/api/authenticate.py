import asyncio
import json
import requests

from lib.api.oauth import getOauthToken


async def authenticate(config, logger, resource="authenticate"):

    oauthToken = await getOauthToken(config)

    # build headers and data payload for upcoming http POST to CULedger.Identity for Onboarding.
    headers = {
            'Content-Type': 'application/json', 
            'Ocp-Apim-Subscription-Key': config["ocp-apim-subscription-key"],
            'clientId': "CentralWalletPOCKeyVault"
            }

    #logger.info("Getting invitation with config: %s", config)

    authEndpoint ="{}member/{}/{}".format(config["endpoint"], config["memberId"], resource)

    authResponse = requests.put(authEndpoint, headers=headers)
    if authResponse.status_code == 200:
        authenticateResponse = authResponse.json()
        logger.info("Success from authenticate: %s", authenticateResponse)
        return authenticateResponse
    else:
        logger.info(f"Error from authenticate:{authResponse}")
