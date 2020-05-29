import asyncio
from time import sleep
import logging
import json
from pathlib import Path
from os import path

from vcx.api.credential import Credential
from vcx.state import State
#from vcx.api.utils import vcx_messages_update_status

from exceptions import TimeOutException

logger = logging.getLogger(__name__)

async def checkOffers(member, connection_to_memberpass, respond_after):
    offers = await Credential.get_offers(connection_to_memberpass)
    if not offers == []:
        if not path.exists(f'./working_config/{member}/{offers[0][0]["msg_ref_id"]}'):
            if respond_after >= 0:
                logger.info("Pausing for %s seconds", respond_after)
                sleep(respond_after)
                logger.info("Resuming after pausing for %s seconds", respond_after)
                await handleOffer(member, connection_to_memberpass, offers)
                Path(f'./working_config/{member}/{offers[0][0]["msg_ref_id"]}').touch()

async def handleOffer(member, connection_to_memberpass, offers):

    credential = await Credential.create('credential', offers[0])
    logger.info("Received credential offer for %s", member)
    await credential.send_request(connection_to_memberpass, 0)

    credential_state = await credential.get_state()
    #TODO need a timeout here to prevent it from polling forever
    while credential_state != State.Accepted:
        sleep(2)
        await credential.update_state()
        credential_state = await credential.get_state()

    #this does not work
    #msg_ref_id = offers[0][0]["msg_ref_id"]
    #await vcx_messages_update_status("[{\"pairwiseDID\":\"" + pw_did + "\",\"uids\":[\"" + msg_ref_id + "\"]}]")
