import asyncio
from vcx.api.disclosed_proof import DisclosedProof
from vcx.state import State
from pathlib import Path
from os import path
from time import sleep
import traceback

async def checkProofs(member, connection_to_memberpass, respond_after, logger):
    try:
        requests = await DisclosedProof.get_requests(connection_to_memberpass)
        if not requests == []:
            for request in requests:
                nonce = request["proof_request_data"]["nonce"]
                if not path.exists(f'./working_config/{member}/{nonce}'):
                    if respond_after >= 0:
                        logger.info("Received proof request, pausing for %s seconds before responding", respond_after)
                        sleep(respond_after)
                        logger.info("Resuming after pausing")
                        await handleProof(member, connection_to_memberpass, request, logger)
                        Path(f'./working_config/{member}/{nonce}').touch()

    except Exception as err:
        tb = traceback.format_exc()
        logger.error(err)
        logger.error(tb)

async def handleProof(member, connection_to_memberpass, request, logger):
    logger.info("Processing proof request")
    proof = await DisclosedProof.create('proof', request)

    credentials = await proof.get_creds()

    # Use the first available credentials to satisfy the proof request
    cred_found = False
    for attr in credentials['attrs']:
        try:
            if len(credentials['attrs'][attr]) > 0:
                cred_found = True
                credentials['attrs'][attr] = {
                    'credential': credentials['attrs'][attr][0]
                }
        except:
            tb = traceback.format_exc()
            logger.error("Error creating response from proof")
            logger.error(tb)

    if cred_found == True:
        await proof.generate_proof(credentials, {})

        await proof.send_proof(connection_to_memberpass)

        proof_state = await proof.get_state()
        while proof_state != State.Accepted:
            sleep(2)
            await proof.update_state()
            proof_state = await proof.get_state()
        logger.info("Found credential and completed processing proof request")
    else:
        logger.info("No credential found for proof request")
