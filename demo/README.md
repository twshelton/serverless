## Demo

This document and associated scripts will show how to setup, run, and tear down the testing harness.

## Local environment with Docker

To run these samples locally, execute the `./docker/run-server.sh` and `./docker/run-client.sh`.  The client script will drop you into a shell where you can execute the samples and they will be handled by the server.  All scipts will execute against `https://stress-dev.culedgerapi.com`

### 1. Initialize

Run `./init_connection.sh` to initialize the service.  This will provision the wallet and connct to the agency and will then be ready to receive connection requests and respond to the IdentityAPI calls.

Overview of config required for initialization.

```json
{
  "memberId": "$MEMBERID",
  "actions": [
    {
      "connect": {
        "respondConnectionOfferAfter": 10,
        "respondCredentialOfferAfter": 10
      }
    },
    {
      "respondAuth": {
        "respondAfter" : 10
      }
    },
    {
      "respondSimpleAuth": {
        "respondAfter" : 10
      }

    },
    {
      "respondProof": {
        "respondAfter" : 10
      }

    }
  ]
}
```
Use the above configuration to tell the emulator how to respond to certain actions.  

This will also create a queue (`connection-{member_id})` where the invitation will be sent after being retrieved from the IdentityAPI.

### 2. Generate Invitation

Run `./generate_invitation.sh` to connect to the IdentityAPI and generate an invitation for the MemberId provided.

### 3. Connect

The results from the above script will be saved locally as invite.json.  Run `./send_invite.sh` to add `invite.json` to the queue for this member.

Overview of config required for connection.

```json
{
    "memberId": "$MEMBERID",
    "invitation": <contents of invite.json>
}
```

### 4. Exercise API

One the above steps are complete, we can use whatever method we would like to exercise the IdentityAPI.  Included are examples for authenticating and secured message scripts.

See `./authenticate.sh` and `./authenticate-simple.sh` for a description of how to make the calls.

### 5. Teardown

Once testing is complete, run `./teardown.sh` to clean up the environment and remove all associated testing artifacts.

Example of config required for teardown.

```json
{
    "memberId": "$MEMBERID"
}
```
