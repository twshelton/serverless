rm sequential*.json
rm sequential*.job

NUMTESTS=1
if [ $# -eq 1 ]
  then
    NUMTESTS=$(seq $1)
fi


for i in $NUMTESTS
do
   MID=`pwgen --no-capitalize`
   echo $MID
   #./test_endpoint.py "sequential1-$MID" &
done

