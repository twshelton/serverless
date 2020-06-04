#!/usr/bin/python3

from time import sleep
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

adapter=None
logger = logging.getLogger(__name__)
connection_to_memberpass=None

async def main():

    decoded = json.loads(base64.b64decode(sys.argv[1]))
    member = decoded["memberId"]
    adapter = CustomAdapter(logger,{'member_id': member}) 
    adapter.info("initializing Vcx for %s", member)
    #create wallet and initialize
    await init(member)

    while True:
        await poll(member, decoded)
        sleep(2)

async def poll(member, decoded):
    global connection_to_memberpass
    try:
        if connection_to_memberpass == None:
            logger.info("checking connection requests for %s", member)
            connect_response_delay = await get_config(decoded, "connect", "respondConnectionOfferAfter")
            connection_to_memberpass = await checkInvitation(member, connect_response_delay)
            logger.info(connection_to_memberpass)
        else:
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
        logging.error(err)
        logging.error(tb)

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
