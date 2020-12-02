import asyncio
from time import sleep
import json
from os import path, getenv
import base64 
import sys

from vcx.api.connection import Connection
from vcx.state import State
from azure.storage.queue import QueueClient

from .exceptions import TimeOutException

async def checkInvitation(member, connect_response_delay, logger):
    connect_str = getenv('AZURE_STORAGE_CONNECTION_STRING')
    queue_client = QueueClient.from_connection_string(connect_str, f'connection-{member}')
    dead_letter = QueueClient.from_connection_string(connect_str, f'connection-error')
    message = queue_client.receive_message(visibility_timeout=10) #s(messages_per_page=1)

    #for batch in messages.by_page():
    #    for message in batch:
    try:
        if message != None:
            decoded = json.loads(base64.b64decode(message.content))
            member = decoded["memberId"]
            connection = await connect(member, decoded["jobId"], decoded["invitation"], connect_response_delay, logger)
            queue_client.delete_message(message)
            logger.info(f'Connected via invitation for memberId: {member} and job: {decoded["jobId"]}')
            return {"jobId": decoded["jobId"], "connection": connection}
    except Exception as ex:
        #TODO need to move this to dead letter queue for review
        dead_letter.send_message(message)
        logger.error("Error Processing Message")
        logger.error(ex)


async def getPwDID(connection_to_memberpass):
    connection = await connection_to_memberpass.serialize()
    return connection["data"]["pw_did"]

async def deserialize(connection):
    return await Connection.deserialize(connection)

async def connect(member, jobId, invitation, respond_after, logger):

    connection_to_memberpass = None

    connectionFile = f'./working_config/{member}/connection.json'
    if not path.exists(connectionFile):
        if respond_after >= 0:
            logger.info("Pausing for %s seconds", respond_after)
            sleep(respond_after)
            logger.info("Resuming after pausing for %s seconds", respond_after)
            #try to make sure we have a valid invitation
            logger.info("connecting based on invite for %s", member)
            connection_to_memberpass = await Connection.create_with_details('memberpass', json.dumps(invitation))
            await connection_to_memberpass.connect('{"use_public_did": true}')

            connection_state = await connection_to_memberpass.update_state()
            while connection_state != State.Accepted:
                logger.info("connection state: %s", connection_state)
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
