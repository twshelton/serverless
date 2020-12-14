import json
import os
import logging
import traceback

from azure.storage.queue import QueueClient
from azure.core.exceptions import ResourceExistsError

def builder(queue_name, logger):

    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    with open('local.settings.json') as settings_json:
        settings = json.load(settings_json)

    queue = f'{settings.get("queue_prefix", "")}-{queue_name}'
    logger.info(f"building queue: {queue}")
    queue_client = QueueClient.from_connection_string(connect_str, queue)
    try:
        queue_client.create_queue()
    except ResourceExistsError:
        logger.info(f"queue already exists: {queue}")
    except Exception as e:
        tb = traceback.format_exc()
        logger.info(f"queue error: {e}")

    return queue_client
