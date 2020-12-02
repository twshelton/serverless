import logging
import time
import sys
import traceback
import os
from opencensus.ext.azure.log_exporter import AzureLogHandler

__version__ = "0.1.0"

class CustomAdapter():

    def __init__(self, name, jobId, memberId, source):

        props = {'custom_dimensions': {'jobId': jobId, 'memberId': memberId, 'source': source}}

        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
        logging.getLogger("vcx").setLevel(logging.CRITICAL)
        logger = logging.getLogger(name)

        key = os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"]

        if len(logger.handlers) > 0:
            for handler in logger.handlers:

              if not isinstance(handler, AzureLogHandler):
                logger.addHandler(AzureLogHandler(
                    connection_string=f'InstrumentationKey={key}')
                )
        else:
            logger.addHandler(AzureLogHandler(
                connection_string=f'InstrumentationKey={key}')
            )

        self.logger = logger
        self.properties = props

    def info(self, message, params=None):
        msg = message
        if params != None:
            msg = message % params

        self.logger.info(msg, extra=self.properties)

    def error(self, message, params=None):
        msg = message
        if params != None:
            msg = message % params

        self.logger.exception(msg, extra=self.properties)

    def release(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            self.logger.removeHandler(handler)

