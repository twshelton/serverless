# Overview

THE CULedger TestHarness is meant to facilitate testing using libVcx from the Credit Union Member perspective.  The two primary components are the MemberPass Coordinator and MemberPass Emulator.  The MemberPass coordinator manages the initialization of the each individual MemberPass Emulator's and can also teardown an environment once testing is complete.

With each initialization, a new Python process is spawned and new crytographic assets are created to be able to respond to certain messages from the MemberPass API.

The following steps are necessary to properly respond to an API request.

### Steps

1. Initialization - A JSON package containing configuration information should be sent to an Azure Queue which the MemberPass Coordinator is watching.  Once received, the coordinator will procedd to set up a MemberPass Emulator to handle messages.
2. /createInvitation - An API call is made to the MemberPass API to get and inviation JSON payload.
3. /poll - Poll the MemberPass API for the invitation paylod.
4. Push the Connection payload to the Azure Queue for this member and the MemberPass Emulator will redpond by accepting the connection.
5. /authenticateSimple - Call the authenticate simple MemberPass API to query the member and get the response from the MemberPass Emulator.
6. /poll - Poll the MemberPass API for the authenticateResponse payload.
7. Push Teardown message onto Azure Queue responsible forteardowns and the Member Emulator will be shut down and will no longer respond to messages from the API.