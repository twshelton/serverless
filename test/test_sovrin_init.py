import pytest
import asyncio

from sovrin.initialize import init

@pytest.mark.asyncio
async def test_init():
    config = {
            'memberId': '42', 
            'walletName': 'test-wallet',
            'walletKey':'test-wallet',
            'institutionName':'Test',
            'institutionLogo':'http://test.com/logo',
            'genesisPath':'/opt/culedgeridentityapi/pool_transactions_live_genesis'
            }
    await init(config)

