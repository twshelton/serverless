import asyncio
from vcx.api.disclosed_proof import DisclosedProof
from vcx.state import State
import logging
from pathlib import Path
from os import path
from time import sleep
logger = logging.getLogger(__name__)

async def checkProofs(member, connection_to_memberpass, respond_after):

    requests = await DisclosedProof.get_requests(connection_to_memberpass)
    if not requests == []:
        for request in requests:
            nonce = request["proof_request_data"]["nonce"]
            if not path.exists(f'./working_config/{member}/{nonce}'):
                if respond_after >= 0:
                    logger.info("Pausing for %s seconds", respond_after)
                    sleep(respond_after)
                    logger.info("Resuming after pausing for %s seconds", respond_after)
                    await handleProof(member, connection_to_memberpass, request)
                    Path(f'./working_config/{member}/{nonce}').touch()

async def handleProof(member, connection_to_memberpass, request):
    logger.info("Received proof request for %s", member)
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
