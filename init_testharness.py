#!/usr/bin/python3

import asyncio
import sys
import os
import logging
import base64
import json
import traceback
import time

from azure.storage.queue import QueueClient

from lib.custom_adapter import CustomAdapter
from lib.queue_builder import builder

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

member = sys.argv[1]
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

async def main():
  try:
    logger = CustomAdapter(__name__, None, member, "TestInitializer")
    init_queue_client = builder("initialize", logger)
    config_ = await config(member)

    logger.info("send init message to queue")
    message = await init_message(member)
    init = await prepare_queue_message(message)
    init_queue_client.send_message(init)
    logger.info("sent init message to queue")
  except Exception as ex:
    with open(f'{member}.job', 'w') as f:
        json.dump({'exception': ex}, f)

    logger.error("Exception")
    tb = traceback.format_exc()
    logger.error(tb)
    logger.error(ex)

async def prepare_queue_message(json_):
    return base64.urlsafe_b64encode(json.dumps(json_).encode()).decode()

async def config(member):
    return {
            "memberId": member, 
            "endpoint1": "https://stress-dev.culedgerapi.com/CULedger/CULedger.Identity/0.3.0/", 
            "endpoint": "https://memberpass-api.azurewebsites.net/api/",
            "endpoint2": "http://localhost:7071/api/",
            "clientSecret": "4oOklTl9zyZGQ.8Et7fUlWh.F0U7BC3y--", 
            "clientId": "b32c5de9-b4d4-431c-b5b8-692c8dff3d13"
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

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    time.sleep(1)
