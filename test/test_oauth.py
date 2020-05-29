import pytest
import asyncio

from api.oauth import getOauthToken as get

CLIENTID="3160b30a-73c9-49ee-b4c0-bf507f9fdba7"
SECRET="Y/PZC4uQtDAPJspCoikD43z8atB3NfSMbQoNIFNHaXc="

@pytest.mark.asyncio
async def test_getOauthToken():
    config = {
            'clientId': CLIENTID, 
            'clientSecret': SECRET
            }
    await get(config)
