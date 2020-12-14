rm -f sequential*.json
rm -f sequential*.job

NUMTESTS=1
if [ $# -eq 1 ]
  then
    NUMTESTS=$(seq $1)
fi

rm -f test_run.txt
touch test_run.txt

MIDS=()

for i in $NUMTESTS
do
   MID=`pwgen --no-capitalize`
   MIDS+=( $MID )
   echo $MID >> test_run.txt
   ./init_testharness.py "sequential1-$MID" &
done

sleep 480

for t in "${MIDS[@]}"
do
   ./test_endpoint.py "sequential1-$t" &
done

