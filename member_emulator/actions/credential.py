import asyncio
import time
import json
from pathlib import Path
from os import path

from vcx.api.credential import Credential
from vcx.state import State
#from vcx.api.utils import vcx_messages_update_status

from .exceptions import TimeOutException

async def checkOffers(member, connection_to_memberpass, respond_after, logger):
    offers = await Credential.get_offers(connection_to_memberpass)
    if not offers == []:
        if not path.exists(f'./working_config/{member}/{offers[0][0]["msg_ref_id"]}'):
            if respond_after >= 0:
                logger.info("Received credential offer, pausing for %s seconds before responding", respond_after)
                asyncio.sleep(respond_after)
                logger.info("Resuming after pausing")
                await handleOffer(member, connection_to_memberpass, offers, logger)
                Path(f'./working_config/{member}/{offers[0][0]["msg_ref_id"]}').touch()

async def handleOffer(member, connection_to_memberpass, offers, logger):

    logger.info("Processing credential offer")
    credential = await Credential.create('credential', offers[0])
    await credential.send_request(connection_to_memberpass, 0)

    credential_state = await credential.get_state()

    timeRemaining = True
    jobComplete = False
    pollInit = time.time()

    while timeRemaining == True and jobComplete == False:
        asyncio.sleep(2)
        if time.time() - pollInit > 1200:
            timeRemaining = False
            logger.info("timeout polling for agent to recognize credential acceptance")
        else:
            await credential.update_state()
            credential_state = await credential.get_state()
            if credential_state == State.Accepted:
                jobComplete = True
                logger.info("Completed processing credential offer")

    #this does not work
    #msg_ref_id = offers[0][0]["msg_ref_id"]
    #await vcx_messages_update_status("[{\"pairwiseDID\":\"" + pw_did + "\",\"uids\":[\"" + msg_ref_id + "\"]}]")
