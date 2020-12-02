import asyncio
import json
import requests

from lib.api.oauth import getOauthToken


async def authenticate(config, logger):

    oauthToken = await getOauthToken(config)

    # build headers and data payload for upcoming http POST to CULedger.Identity for Onboarding.
    headers = {
            'Content-Type': 'application/json', 
            'Authorization': 'Bearer ' + oauthToken,
            'clientId': "CentralWalletPOCKeyVault"
            }

    #logger.info("Getting invitation with config: %s", config)

    code="nMeOMariKmmEJU7AqiV0/CJjITxGM411YVW4d1lrGaBwY9nFT6TqmA=="
    authEndpoint ="{}member/{}/authenticate?code={}".format(config["endpoint"], config["memberId"],code)

    authResponse = requests.put(authEndpoint, headers=headers)
    if authResponse.status_code == 200:
        authenticateResponse = authResponse.json()
        logger.info("Success from authenticate: %s", authenticateResponse)
        return authenticateResponse
    else:
        logger.info("Error from authenticate")
