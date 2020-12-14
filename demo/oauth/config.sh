#!/bin/bash

# The following variables must be provided in order for the script to run properly
# ============================================================================================
CLIENTID="b32c5de9-b4d4-431c-b5b8-692c8dff3d13"
SECRET="4oOklTl9zyZGQ.8Et7fUlWh.F0U7BC3y--"
TENANTID="e7b6a690-d322-4085-b6d6-d0a4f70f0d7b"
ENDPOINT="http://localhost:7071/api"
ENDPOINT1="https://memberpass-api.azurewebsites.net/api"
CODE="nMeOMariKmmEJU7AqiV0/CJjITxGM411YVW4d1lrGaBwY9nFT6TqmA=="
# ============================================================================================

echo "${CLIENTID:?REQUIRED: client id provided by CULedger}" > /dev/null
echo "${SECRET:?REQUIRED: client secret provided by CULedger}" > /dev/null
echo "${TENANTID:?REQUIRED: tenant id provided by CULedger}" > /dev/null
echo "${ENDPOINT:?REQUIRED: api endpoint provided by CULedger}" > /dev/null

command -v jq >/dev/null 2>&1 || { echo >&2 "I require jq but it's not installed. See https://stedolan.github.io/jq/ for installation instructions"; exit 1; }
