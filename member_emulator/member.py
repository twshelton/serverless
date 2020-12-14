#!/usr/bin/python3

import time
import asyncio
import logging
import json 
import traceback
import sys
import base64
from custom_adapter import CustomAdapter

from sovrin.initialize import init
from actions.connect import checkInvitation
from actions.messages import checkMessages
from actions.credential import checkOffers
from actions.proofs import checkProofs

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
logging.getLogger("vcx").setLevel(logging.CRITICAL)

connection_to_memberpass=None
jobId=None

async def main():
    decoded = json.loads(base64.b64decode(sys.argv[1]))
    member = decoded["memberId"]
    logger = CustomAdapter(__name__, jobId, member, "TestHarness")
    logger.info("initializing Vcx")

    #create wallet and initialize
    await init(member, logger)
    time_start = time.time()
    while True:
        # set 45 second 
        await poll(member, decoded, logger)
        if jobId != None:
            logger = CustomAdapter(__name__, jobId, member, "TestHarness")

        time.sleep(5)

async def poll(member, decoded, logger):
    global connection_to_memberpass
    global jobId
    try:
        if connection_to_memberpass == None:
            logger.info(f"checking for connection requests: {member}")
            connect_response_delay = await get_config(decoded, "connect", "respondConnectionOfferAfter")
            connected = await checkInvitation(member, connect_response_delay, logger)
            if connected != None:
                jobId = connected["jobId"]
                connection_to_memberpass = connected["connection"]
                logger.info("connection established: %s", connection_to_memberpass)
        else:
            logger.info(f"checking credential offers for {member}")
            offer_response_delay = await get_config(decoded, "respondAuth", "respondAfter")
            await checkOffers(member, connection_to_memberpass, offer_response_delay, logger)

            logger.info(f"checking proof requests for {member}")
            proof_response_delay = await get_config(decoded, "respondProof", "respondAfter")
            await checkProofs(member, connection_to_memberpass, proof_response_delay, logger)

            #logger.info("checking secured messages for %s", member)
            #message_response_delay = await get_config(decoded, "respondSimpleAuth", "respondAfter")
            #await checkMessages(member, connection_to_memberpass, message_response_delay, logger)

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
    time.sleep(1)
