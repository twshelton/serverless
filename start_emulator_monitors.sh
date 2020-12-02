#!/usr/bin/python3

import asyncio
import sys
import os
import base64
import json
import glob
from pathlib import Path
import subprocess
from time import sleep
import traceback
import shutil
from azure.storage.queue import QueueClient
import signal

from lib.custom_adapter import CustomAdapter

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
init_queue_client = QueueClient.from_connection_string(connect_str, "initialize")
teardown_queue_client = QueueClient.from_connection_string(connect_str, "teardown")
init_dead_letter = QueueClient.from_connection_string(connect_str, "initialize-error")
teardown_dead_letter = QueueClient.from_connection_string(connect_str, "teardown-error")
member = None
members = {}

files = glob.glob('./running/*')
for f in files:
    shutil.rmtree(f)

async def main(logger):
	logger.info("Looking for jobs to process")
	while True:
		await check_init_queue(logger)
		await check_teardown_queue(logger)
		sleep(2)

async def check_init_queue(logger):
    try:
        messages = init_queue_client.receive_messages(messages_per_page=5)
        for batch in messages.by_page():
            for message in batch:
                try:
                    decoded = json.loads(base64.b64decode(message.content))
                    member = decoded["memberId"]
                    if not os.path.exists(f'./running/{member}'):
                        queue_name = "connection-" + member
                        member_queue = QueueClient.from_connection_string(connect_str, queue_name)
                        logger.info(f"Creating queue: {queue_name}")
                        member_queue.create_queue()
                        logger.info(f"Created queue: {queue_name}")

                        proc = subprocess.Popen(["./member_emulator/member.py", message.content, member,"&"])
                        members[member] = proc
                        Path(f'./running/{member}').touch()
                    else:
                        logger.info(f"Duplicate member {member} -- already running")

                    init_queue_client.delete_message(message)
                except Exception as ex:
                    #TODO need to move this to dead letter queue for review
                    init_dead_letter.send_message(message)
                    tb = traceback.format_exc()
                    logger.error(tb)
                    logger.error("Error Processing Message")
                    logger.error(ex)

    except Exception as ex:
        logger.error("Exception")
        tb = traceback.format_exc()
        logger.error(tb)
        logger.error(ex)

async def check_teardown_queue(logger):
    try:
        messages = teardown_queue_client.receive_messages(messages_per_page=5)
        for batch in messages.by_page():
            for message in batch:
                try:
                    decoded = json.loads(base64.b64decode(message.content))
                    member = decoded["memberId"]
                    proc = members.get(member)
                    if not proc == None:
                      #remove running entry
                      if os.path.exists(f'./running/{member}'):
                        os.remove(f'./running/{member}')
                    
                      #remove working_data entry
                      shutil.rmtree(f'./working_config/{member}', ignore_errors=True)
                      #remove connection-{member} queue
                      queue_name = "connection-" + member
                      member_queue = QueueClient.from_connection_string(connect_str, queue_name)
                      try:
                        member_queue.delete_queue()
                      except:
                        logger.error(f"error deleting queue: {queue_name}")

                      proc.terminate()
                      teardown_queue_client.delete_message(message)
                    else:
                      logger.info(f"Unable to locate member to teardown: {member}")

                except Exception as ex:
                    teardown_dead_letter.send_message(message)
                    tb = traceback.format_exc()
                    logger.error(tb)
                    logger.error("Error Processing Message")
                    logger.error(ex)

    except Exception as ex:
        logger.error("Exception")
        tb = traceback.format_exc()
        logger.error(tb)
        logger.error(ex)


if __name__ == '__main__':
  try:
    loop = asyncio.get_event_loop()
    logger = CustomAdapter(__name__, None, None, "TestHarnessManager")
    loop.run_until_complete(main(logger))
    sleep(1)
  except KeyboardInterrupt:
    print('Interrupted')
    try:
      for m,pid in members.items():
        queue_name = "connection-" + m
        member_queue = QueueClient.from_connection_string(connect_str, queue_name)
        try:
          member_queue.delete_queue()
        except:
          logger.error("error deleting queue: %s", queue_name)
    except SystemExit:
      tb = traceback.format_exc()
      logger.error(tb)
      os._exit(0)
