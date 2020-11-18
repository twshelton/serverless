#!/bin/bash

while getopts :i: opt; do
  case "${opt}" in
    i) MEMBERID=`echo ${OPTARG} | tr '[:upper:]' '[:lower:]'`
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

if [ -z $MEMBERID ]; then
  echo "===================================================================================="
  echo "USAGE:"
  echo "       -i: Member Identifier"
  echo ""
  echo "  Please provide memberId as it is required for this procedure"
  echo "===================================================================================="
  exit
fi

mkdir -p $MEMBERID

echo "Initializing connection for $MEMBERID through headless testing environment"
./init_connection.sh -i $MEMBERID
echo "Generating invitation to establish connection with headless testing environment"
./generate_invitation.sh -i $MEMBERID
echo "Send invitation to headless testing environment"
./send_invite.sh -i $MEMBERID
sleep 45
./get_member.sh -i $MEMBERID
echo "Authenticating over established connection"
./authenticate.sh -i $MEMBERID

