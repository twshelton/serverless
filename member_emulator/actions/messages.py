import asyncio
from time import sleep
import logging
import base64
import datetime
import json
from actions.connect import getPwDID
from custom_adapter import CustomAdapter

from vcx.api.utils import vcx_messages_download, vcx_messages_update_status
from vcx.state import State

from exceptions import TimeOutException

logger = logging.getLogger(__name__)

async def checkMessages(member, connection_to_memberpass, respond_after):
    adapter = CustomAdapter(logger,{'member_id': member}) 
    pw_did = await getPwDID(connection_to_memberpass)
    secured = await vcx_messages_download('MS-103', '', None)
    smsgs = json.loads(secured.decode('utf-8'))
    now = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%S+0000")
    if not smsgs == []:
        for msg in smsgs[0]["msgs"]:
            if msg["type"] == "Question":
                if respond_after >= 0:
                    adapter.info("Received secured message, pausing for %s seconds before responding", respond_after)
                    sleep(respond_after)
                    adapter.info("Resuming after pausing")
                    adapter.info("Processing  secured message")
                    question = json.loads(json.loads(msg["decryptedPayload"])["@msg"])
                    #TODO handle which response to send back
                    data = base64.b64encode(question['valid_responses'][1]['nonce'].encode())
                    signature = await connection_to_memberpass.sign_data(data)
                    answer = {
                        "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/committedanswer/1.0/answer",
                        "response.@sig": {
                            "signature": base64.b64encode(signature).decode('utf-8'),
                            "sig_data": data.decode('utf-8'),
                            "timestamp": now
                            }
                        }
                    msg_id = await connection_to_memberpass.send_message(json.dumps(answer), "Answer", "Consumer answer sent")
                    await vcx_messages_update_status("[{\"pairwiseDID\":\"" + pw_did + "\",\"uids\":[\"" + msg["uid"] + "\"]}]")
                    adapter.info("Completed processing secured message")

