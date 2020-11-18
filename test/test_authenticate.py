
import pytest
import asyncio
import sys

sys.path.append("/opt/culedger-core/")
print(sys.path)
from lib.api.authenticate import authenticate as get

@pytest.mark.asyncio
async def test_getOauthToken():
    config = {
            "clientSecret": "4oOklTl9zyZGQ.8Et7fUlWh.F0U7BC3y--", 
            "clientId": "b32c5de9-b4d4-431c-b5b8-692c8dff3d13",
            'memberId': '1234',
            "endpoint": "https://stress-dev.culedgerapi.com/CULedger/CULedger.Identity/0.3.0/", 
            }
    await get(config)
