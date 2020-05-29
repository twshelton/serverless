import asyncio
from time import sleep
import logging
import json
from os import path

from vcx.api.connection import Connection
from vcx.state import State

from exceptions import TimeOutException

logger = logging.getLogger(__name__)

async def getPwDID(connection_to_memberpass):
    connection = await connection_to_memberpass.serialize()
    return connection["data"]["pw_did"]

async def deserialize(connection):
    return await Connection.deserialize(connection)

async def connect(member, invitation, respond_after):

    connection_to_memberpass = None

    connectionFile = f'./working_config/{member}/connection.json'
    if not path.exists(connectionFile):
        if respond_after >= 0:
            logger.info("Pausing for %s seconds", respond_after)
            sleep(respond_after)
            logger.info("Resuming after pausing for %s seconds", respond_after)
            #try to make sure we have a valid invitation
            if "id" in invitation:
                logger.info("connecting based on invite for %s", member)
                connection_to_memberpass = await Connection.create_with_details('memberpass', json.dumps(invitation))
                await connection_to_memberpass.connect('{"use_public_did": true}')

                connection_state = await connection_to_memberpass.update_state()
                while connection_state != State.Accepted:
                    sleep(2)
                    await connection_to_memberpass.update_state()
                    connection_state = await connection_to_memberpass.get_state()

                connection = await connection_to_memberpass.serialize()
                logger.info("saving connection for %s", member)
                f = open(connectionFile, "w")
                f.write(json.dumps(connection))
                f.close()
    else:
        logger.info("Load existing connection file for %s", member)
        connection_string = open(connectionFile,'r').read()
        connection = json.loads(connection_string)
        connection_to_memberpass = await deserialize(connection)

    logger.info("Connection is established")
    return connection_to_memberpass
