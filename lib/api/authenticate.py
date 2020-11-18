import asyncio
import json
import requests
import logging

from lib.api.oauth import getOauthToken

from lib.custom_adapter import CustomAdapter

async def authenticate(config):

    logger = logging.getLogger(__name__)
    adapter = CustomAdapter(logger,{'member_id': config["memberId"]}) 

    oauthToken = await getOauthToken(config)

    # build headers and data payload for upcoming http POST to CULedger.Identity for Onboarding.
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + oauthToken}

    #logger.info("Getting invitation with config: %s", config)

    authEndpoint ="{}member/{}/authenticate".format(config["endpoint"], config["memberId"])

    authResponse = requests.put(authEndpoint, headers=headers)
    if authResponse.status_code == 200:
        authenticateResponse = authResponse.json()
        adapter.info("Success from authenticate: %s", authenticateResponse)
        return authenticateResponse
    else:
        adapter.info("Error from authenticate")
