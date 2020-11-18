#!/usr/bin/python3

import asyncio
import sys
import os
import logging
import base64
import json
from time import sleep
import traceback
from azure.storage.queue import QueueClient

from lib.api.invite import createInvitation
from lib.api.authenticate import authenticate
from lib.api.authenticate_simple import authenticate as simple

base_path = os.path.abspath('')
sys.path.append(base_path + "/lib/")
print(sys.path)

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

member = sys.argv[1]
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
init_queue_client = QueueClient.from_connection_string(connect_str, "initialize")
connect_queue_client = QueueClient.from_connection_string(connect_str, f'connection-{member}')
teardown_queue_client = QueueClient.from_connection_string(connect_str, "teardown")

async def main():
  try:
    config_ = await config(member)

    logger.info("send init message to queue")
    message = await init_message(member)
    init = await prepare_queue_message(message)
    init_queue_client.send_message(init)

    logger.info("get invitation from API")
    invite = await createInvitation(config_)
    #
    logger.info("send connect message to queue")
    sleep(2)
    conn_msg = await connection_message(member, json.loads(invite))
    connection = await prepare_queue_message(conn_msg)
    connect_queue_client.send_message(connection)
    sleep(20) 
    logger.info("authenticate through API")
    authDetails = await authenticate(config_)
    if authDetails == None:
        logger.info("Authenticate failed")
    else:
        logger.info("Authenticate succeeded!")

    #logger.info("auth-simple through API")
    #authSimple = await simple(config_)
    #if authSimple == None:
    #    logger.info("Authenticate failed")

    #logger.info("send teardown message to queue")
    #sleep(20)
    #message = await teardown_message(member)
    #teardown = await prepare_queue_message(message)
    #teardown_queue_client.send_message(teardown)

  except Exception as ex:
    logger.error("Exception")
    tb = traceback.format_exc()
    logger.error(tb)
    logger.error(ex)

async def prepare_queue_message(json_):
    return base64.urlsafe_b64encode(json.dumps(json_).encode()).decode()

#async def config(member):
#    return {
#            "memberId": member, 
#            "endpoint": "http://localhost:8082/CULedger/CULedger.Identity/0.3.0/", 
#            "clientSecret": "asvMk5RV/2Qp5WW4HHDu95Ft6dFLAq8qCjFvzL8nLic=", 
#            "clientId": "5eed2130-1e01-4996-9e1c-16cc5f2e84ed"
#            }
async def config(member):
    return {
            "memberId": member, 
            "endpoint": "https://stress-dev.culedgerapi.com/CULedger/CULedger.Identity/0.3.0/", 
            "clientSecret": "4oOklTl9zyZGQ.8Et7fUlWh.F0U7BC3y--", 
            "clientId": "b32c5de9-b4d4-431c-b5b8-692c8dff3d13"
            }

async def connection_message(member, invitation):
    return {
            "memberId": member,
            "invitation": invitation
            }


async def teardown_message(member):
    return {
            "memberId": member
            }

async def init_message(member):
    return {
            "memberId": member,
            "actions": [
                {
                    "connect": {
                        "respondConnectionOfferAfter": 1,
                        "respondCredentialOfferAfter": 1
                        }
                    },
                {
                    "respondAuth": {
                        "respondAfter" : 1
                        }
                    },
                {
                    "respondSimpleAuth": {
                        "respondAfter" : 10
                        }

                    },
                {
                    "respondProof": {
                        "respondAfter" : 10
                        }

                    }
                ]
            }

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    sleep(1)
