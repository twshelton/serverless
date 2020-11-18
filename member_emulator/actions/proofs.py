import asyncio
from vcx.api.disclosed_proof import DisclosedProof
from vcx.state import State
import logging
from pathlib import Path
from os import path
from time import sleep
from custom_adapter import CustomAdapter
import traceback

logger = logging.getLogger(__name__)
adapter=None

async def checkProofs(member, connection_to_memberpass, respond_after):
    global adapter
    adapter = CustomAdapter(logger,{'member_id': member}) 
    try:
        requests = await DisclosedProof.get_requests(connection_to_memberpass)
        if not requests == []:
            for request in requests:
                nonce = request["proof_request_data"]["nonce"]
                if not path.exists(f'./working_config/{member}/{nonce}'):
                    if respond_after >= 0:
                        adapter.info("Received proof request, pausing for %s seconds before responding", respond_after)
                        sleep(respond_after)
                        adapter.info("Resuming after pausing")
                        await handleProof(member, connection_to_memberpass, request)
                        Path(f'./working_config/{member}/{nonce}').touch()

    except Exception as err:
        tb = traceback.format_exc()
        logging.error(err)
        logging.error(tb)

async def handleProof(member, connection_to_memberpass, request):
    adapter.info("Processing proof request")
    proof = await DisclosedProof.create('proof', request)

    credentials = await proof.get_creds()

    # Use the first available credentials to satisfy the proof request
    for attr in credentials['attrs']:
        credentials['attrs'][attr] = {
            'credential': credentials['attrs'][attr][0]
        }

    await proof.generate_proof(credentials, {})

    await proof.send_proof(connection_to_memberpass)

    proof_state = await proof.get_state()
    while proof_state != State.Accepted:
        sleep(2)
        await proof.update_state()
        proof_state = await proof.get_state()


    adapter.info("Completed processing proof request")
