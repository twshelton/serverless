import asyncio
import json
from ctypes import cdll
import logging
from os import path,mkdir,getenv

from demo_utils import file_ext

from vcx.api.utils import vcx_agent_provision
from vcx.api.vcx_init import vcx_init_with_config

async def init(member, logger):

    payment_plugin = cdll.LoadLibrary('libnullpay' + file_ext())
    payment_plugin.nullpay_init()

    vcxConfigFile = f'./working_config/{member}/vcxconfig.json'

    if not path.exists(vcxConfigFile):
        logger.info("Provision new agent and wallet")
        wallet_name = f'wallet-{member}'
        wallet_key = f'wallet-key-{member}'
        provisionVars = await provisionConfig(wallet_name, wallet_key)
        vcxconfig = await vcx_agent_provision(json.dumps(provisionVars))
        vcxconfig = json.loads(vcxconfig)

        # Set some additional configuration options specific to alice
        vcxconfig['institution_name'] = getenv("INSTITUTION_NAME")
        vcxconfig['institution_logo_url'] = getenv("INSTITUTION_LOGO")
        vcxconfig['genesis_path'] = getenv("GENESIS_PATH")
        vcxconfig['payment_method'] = 'null'

        vcxconfig = json.dumps(vcxconfig)
        mkdir(f'./working_config/{member}')
        f = open(vcxConfigFile, "w")
        f.write(vcxconfig)
        f.close()
    else:
        logger.info("Load existing config for agent and wallet")
        vcxconfig = open(vcxConfigFile,'r').read()

    logger.info("Initialize libvcx with configuration")
    await vcx_init_with_config(vcxconfig)

async def provisionConfig(wallet_name, wallet_key): 
    return {
        'agency_url': 'https://hea001.hs.evernym.com',
        'agency_did': 'QAxGCiizb9VZNiwZEBJzon',
        'agency_verkey': 'DdVzquhStrxauGmVTBTDEVfm5q6aSbLsj9CHJQkHUTsy',
        'agent_seed': None,
        'enterprise_seed': None,
        'wallet_name': wallet_name,
        'wallet_key': wallet_key
    }
