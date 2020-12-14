#!/usr/bin/python3

import asyncio
import sys
import os
import logging
import base64
import json
from time import sleep
import traceback
import time

from azure.storage.queue import QueueClient

from lib.api.invite import createInvitation
from lib.api.member import member as get_member
from lib.api.authenticate import authenticate
from lib.api.authenticate_simple import authenticate as simple
from lib.custom_adapter import CustomAdapter
from lib.queue_builder import builder

base_path = os.path.abspath('')
sys.path.append(base_path + "/lib/")
print(sys.path)

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

member = sys.argv[1]
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

async def main():
  try:
    logger = CustomAdapter(__name__, None, member, "TestOrchestrator")

    #init_queue_client = builder("initialize", logger)
    teardown_queue_client = builder("teardown", logger)

    connect_queue_client = QueueClient.from_connection_string(connect_str, f'connection-{member}')
    
    config_ = await config(member)
    
    #logger.info("send init message to queue")
    #message = await init_message(member)
    #init = await prepare_queue_message(message)
    #init_queue_client.send_message(init)

    logger.info("get invitation from API")
    invite = await createInvitation(config_, logger)
    logger.info(f"received invitation: {invite}")
    logger.info("send connect message to queue")
    #fun starts here
    if invite != None:
        if invite.get("jobId", None) != None:
            jobId = invite["jobId"]
            start_time = time.time()
            logger = CustomAdapter(__name__, jobId, member, "TestOrchestrator")
            with open(f'{member}.job', 'w') as f:
                json.dump(invite, f)

            conn_msg = await connection_message(member, invite)
            connection = await prepare_queue_message(conn_msg)
            connect_queue_client.send_message(connection)
            sleep(30) 
            authDetails = {}
            logger.info("get member through API")
            memDetails = await get_member(config_, logger)
            if memDetails == None:
                logger.info("get member failed")
            else:
                logger.info("get member succeeded!")
            #logger.info("authenticate through API")
            #authDetails = await authenticate(config_, logger)
            #if authDetails == None:
            #    logger.info("Authenticate failed")
            #else:
            #    logger.info("Authenticate succeeded!")

            #logger.info("auth-simple through API")
            #authSimple = await simple(config_)
            #if authSimple == None:
            #    logger.info("Authenticate failed")

            logger.info("send teardown message to queue")
            message = await teardown_message(member)
            teardown = await prepare_queue_message(message)
            teardown_queue_client.send_message(teardown)
            end_time = time.time()
            jobOutput = {
                    'jobId': jobId,
                    'timeToComplete': end_time-start_time,
                    'results': memDetails
                    }
            with open(f'{member}.json', 'w') as f:
                json.dump(jobOutput, f)

            logger.info(f"Test Results:{json.dumps(jobOutput)}")
        else:
            logger.info("problem with invite")
            logger.info(invite)
    else:
        logger.info("problem with invite: NoneType")

  except Exception as ex:
    logger.error("Exception")
    tb = traceback.format_exc()
    logger.error(tb)
    logger.error(ex)


async def config(member):
    return {
            "memberId": member,
            "endpoint1": "https://stress-dev.culedgerapi.com/CULedger/CULedger.Identity/0.3.0/",
            "endpoint": "https://apim-culedger-test.azure-api.net/memberpass-api/",
            "endpoint2": "https://memberpass-api.azurewebsites.net/api/",
            "clientId": "CentralWalletPOCKeyVault",
            "ocp-apim-subscription-key": "6311bd64cdce49c08577c0c8f75d54d9"
            }


async def prepare_queue_message(json_):
    return base64.urlsafe_b64encode(json.dumps(json_).encode()).decode()

async def connection_message(member, invitation):
    return {
            "memberId": member,
            "invitation": json.loads(invitation["invitationJSON"]),
            "jobId": invitation["jobId"]
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
                        "respondAfter" : 1
                        }

                    },
                {
                    "respondProof": {
                        "respondAfter" : 1
                        }

                    }
                ]
            }


async def teardown_message(member):
    return {
            "memberId": member
            }

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    sleep(1)
