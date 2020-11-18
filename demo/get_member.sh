
#!/bin/bash

set -e

while getopts :i: opt; do
  case "${opt}" in
    i) MEMBERID=${OPTARG}
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

MEMBER=`cd /opt/culedger-core/demo/oauth/ && ./get_member.sh -i $MEMBERID`
echo $MEMBER > $MEMBERID/membert_status.json
MEMBER_STATUS=`echo $MEMBER | jq -r .memberStatus`
[ $? -eq 0 ] && echo "$MEMBER" || echo "Not Found"
