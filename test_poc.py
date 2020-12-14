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

    init_queue_client = builder("initialize", logger)
    teardown_queue_client = builder("teardown", logger)

    connect_queue_client = QueueClient.from_connection_string(connect_str, f'connection-{member}')

    logger.info("send init message to queue")
    message = await init_message(member)
    init = await prepare_queue_message(message)
    init_queue_client.send_message(init)

    logger.info("get poc_invitation from API")
    invite = await createInvitation(config_, logger)
    logger.info(f"received poc_invitation: {invite}")
    logger.info("send connect message to queue")
    #fun starts here
    if invite != None:
        if invite.get("jobId", None) != None:
            try:
                jobId = invite["jobId"]
                start_time = time.time()
                logger = CustomAdapter(__name__, jobId, member, "TestOrchestrator")
                with open(f'{member}.job', 'w') as f:
                    json.dump(invite, f)

                conn_msg = await connection_message(member, invite)
                connection = await prepare_queue_message(conn_msg)
                sleep(5) 
                connect_queue_client.send_message(connection)

                #logger.info("poc_authenticate through API")
                #authDetails = await authenticate(config_, logger, "pocauth")
                #if authDetails == None:
                #    logger.info("poc_Authenticate failed")
                #else:
                #    logger.info("poc_Authenticate succeeded!")

                logger.info("auth-simple through API")
                authSimple = await simple(config_, logger)
                if authSimple == None:
                    logger.info("poc_Authenticate failed")
                else:
                    logger.info("poc_Authenticate succeeded!")

                logger.info("send teardown message to queue")
                message = await teardown_message(member)
                teardown = await prepare_queue_message(message)
                teardown_queue_client.send_message(teardown)
                end_time = time.time()
                jobOutput = {
                        'jobId': jobId,
                        'timeToComplete': end_time-start_time,
                        'results': authSimple
                        }
                with open(f'{member}.json', 'w') as f:
                    json.dump(jobOutput, f)

                logger.info(f"Test Results:{json.dumps(jobOutput)}")
            except Exception as ex:
                end_time = time.time()
                jobOutput = {
                        'jobId': jobId,
                        'timeToComplete': end_time-start_time,
                        'results': str(ex)
                        }
                with open(f'{member}.json', 'w') as f:
                    json.dump(jobOutput, f)

                logger.error("Exception while processing inviation")
                tb = traceback.format_exc()
                logger.error(tb)
                logger.error(ex)
        else:
            logger.info("problem with invite")
            logger.info(invite)
    else:
        logger.info("problem with invite: NoneType")

  except Exception as ex:
    with open(f'{member}.job', 'w') as f:
        json.dump({'exception': ex}, f)

    logger.error("Exception")
    tb = traceback.format_exc()
    logger.error(tb)
    logger.error(ex)

async def prepare_queue_message(json_):
    return base64.urlsafe_b64encode(json.dumps(json_).encode()).decode()

async def connection_message(member, invitation):
    return {
            "memberId": member,
            "invitation": json.loads(invitation["invitationJSON"]),
            "jobId": invitation["jobId"]
            }


async def teardown_message(member):
    return {
            "memberId": member
            }

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    sleep(1)
