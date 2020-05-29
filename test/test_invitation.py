import pytest
import asyncio

from api.invite import createInvitation as get

CLIENTID="3160b30a-73c9-49ee-b4c0-bf507f9fdba7"
SECRET="Y/PZC4uQtDAPJspCoikD43z8atB3NfSMbQoNIFNHaXc="

@pytest.mark.asyncio
async def test_getOauthToken():
    config = {
            'clientId': CLIENTID, 
            'clientSecret': SECRET,
            'memberId': '1234',
            'endpoint': "http://localhost:8082/CULedger/CULedger.Identity/0.3.0/"
            }
    await get(config)
