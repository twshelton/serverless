#!/usr/bin/env python

from time import sleep
import asyncio
import logging
import json 
import traceback
import sys
import base64

from sovrin.initialize import init
from actions.connect import connect
from actions.messages import checkMessages
from actions.credential import checkOffers
from actions.proofs import checkProofs

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("vcx").setLevel(logging.CRITICAL)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

async def main():

    decoded = json.loads(base64.b64decode(sys.argv[1]))
    member = decoded["memberId"]
    logger.info("initializing Vcx for %s", member)
    await init(member)

    connect_response_delay = await get_config(decoded, "connect", "respondConnectionOfferAfter")
    logger.info("Response delay for connect: %s", connect_response_delay)
    connection_to_memberpass = await connect(member, decoded["invitation"], connect_response_delay)

    while True:
        await poll(member, connection_to_memberpass, decoded)
        sleep(2)

async def poll(member, connection_to_memberpass, decoded):

    try:
        #logger.info("checking credential offers for %s", member)
        offer_response_delay = await get_config(decoded, "respondAuth", "respondAfter")
        await checkOffers(member, connection_to_memberpass, offer_response_delay)

        #logger.info("checking proof requests for %s", member)
        proof_response_delay = await get_config(decoded, "respondProof", "respondAfter")
        await checkProofs(member, connection_to_memberpass, proof_response_delay)

        #logger.info("checking secured messages for %s", member)
        message_response_delay = await get_config(decoded, "respondSimpleAuth", "respondAfter")
        await checkMessages(member, connection_to_memberpass, message_response_delay)

    except Exception as err:
        tb = traceback.format_exc()
        logger.error(err)
        logger.error(tb)

async def get_config(config, desired, timer):
    for action in config["actions"]:
        if desired in action:
            respond = action[desired]
            if timer in respond:
                return respond[timer]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    sleep(1)
