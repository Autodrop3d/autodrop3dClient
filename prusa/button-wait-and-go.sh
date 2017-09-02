#! /bin/bash

while [ true ]
do
   CODE=`gpio -g read 23`
   if [ $CODE -ge 1 ]; then
      echo "kerblam"
      break
   fi
   echo "waiting..."
   sleep 0.1
done

echo "kerblam!"
