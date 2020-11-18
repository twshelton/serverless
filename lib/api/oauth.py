import asyncio
import json
import requests
import logging
import urllib3

OAUTH_URL="https://login.microsoftonline.com/e7b6a690-d322-4085-b6d6-d0a4f70f0d7b/oauth2/token"
urllib3.disable_warnings()

async def getOauthToken(config):

    logger = logging.getLogger(__name__)

    data = {'grant_type': 'client_credentials', 'client_secret': config["clientSecret"], 'client_id' : config["clientId"], 'redirect_uri': ""}

    logger.info("requesting access token")

    access_token_response = requests.post(OAUTH_URL, data=data, verify=False, allow_redirects=False)

    res = access_token_response.json() #.access_token

    if "error" in res:
        raise Exception(res)

    oauth_token = res["access_token"]

    return oauth_token

