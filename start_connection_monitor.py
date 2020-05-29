#!/usr/bin/env python

import asyncio
import sys
import os
import logging
import base64
import json
import glob
from pathlib import Path
import subprocess
from time import sleep

from azure.storage.queue import QueueClient

base_path = os.path.abspath('')
sys.path.append(base_path + "/lib/")

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
queue_client = QueueClient.from_connection_string(connect_str, "connection")

member = None

files = glob.glob('./running/*')
for f in files:
    os.remove(f)

async def main():

    while True:
        await check_queue()
        sleep(2)

async def check_queue():
    try:
        messages = queue_client.receive_messages(messages_per_page=5)
        for batch in messages.by_page():
            for message in batch:
                try:
                    decoded = json.loads(base64.b64decode(message.content))
                    member = decoded["memberId"]
                    if not os.path.exists(f'./running/{member}'):
                        proc = subprocess.Popen(["./member_emulator/member.py", message.content, member,"&"])
                        Path(f'./running/{member}').touch()
                    else:
                        logger.info("Duplicate member %s -- already running", member)

                    queue_client.delete_message(message)
                except Exception as ex:
                    #TODO need to move this to dead letter queue for review
                    queue_client.delete_message(message)
                    logger.error("Error Processing Message")
                    logger.error(ex)

    except Exception as ex:
        logger.error("Exception")
        logger.error(ex)

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        sleep(1)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
