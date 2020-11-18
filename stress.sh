for i in {1..10}
do
   MID=`pwgen --no-capitalize`
   echo $MID
   ./test_endpoint.py "sequential2-$i"
done
