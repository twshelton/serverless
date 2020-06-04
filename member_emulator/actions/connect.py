import asyncio
from time import sleep
import logging
import json
from os import path, getenv
from vcx.api.connection import Connection
from vcx.state import State
import sys
from exceptions import TimeOutException
sys.path.append("..")
from custom_adapter import CustomAdapter
from azure.storage.queue import QueueClient
import base64 

logger = logging.getLogger(__name__)

async def checkInvitation(member, connect_response_delay):
    connect_str = getenv('AZURE_STORAGE_CONNECTION_STRING')
    queue_client = QueueClient.from_connection_string(connect_str, f'connection-{member}')
    dead_letter = QueueClient.from_connection_string(connect_str, f'connection-error')
    messages = queue_client.receive_messages(messages_per_page=5)
    for batch in messages.by_page():
        for message in batch:
            try:
                decoded = json.loads(base64.b64decode(message.content))
                member = decoded["memberId"]
                connection = await connect(member, decoded["invitation"], connect_response_delay)
                queue_client.delete_message(message)
                return connection
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

async def connect(member, invitation, respond_after):

    adapter = CustomAdapter(logger,{'member_id': member}) 
    connection_to_memberpass = None

    connectionFile = f'./working_config/{member}/connection.json'
    if not path.exists(connectionFile):
        if respond_after >= 0:
            adapter.info("Pausing for %s seconds", respond_after)
            sleep(respond_after)
            adapter.info("Resuming after pausing for %s seconds", respond_after)
            #try to make sure we have a valid invitation
            if "id" in invitation:
                adapter.info("connecting based on invite for %s", member)
                connection_to_memberpass = await Connection.create_with_details('memberpass', json.dumps(invitation))
                await connection_to_memberpass.connect('{"use_public_did": true}')

                connection_state = await connection_to_memberpass.update_state()
                while connection_state != State.Accepted:
                    sleep(2)
                    await connection_to_memberpass.update_state()
                    connection_state = await connection_to_memberpass.get_state()

                connection = await connection_to_memberpass.serialize()
                adapter.info("saving connection for %s", member)
                f = open(connectionFile, "w")
                f.write(json.dumps(connection))
                f.close()
    else:
        adapter.info("Load existing connection file for %s", member)
        connection_string = open(connectionFile,'r').read()
        connection = json.loads(connection_string)
        connection_to_memberpass = await deserialize(connection)

    adapter.info("Connection is established")
    return connection_to_memberpass
