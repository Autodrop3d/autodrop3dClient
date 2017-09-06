#! /bin/bash
COUNT=0
while [ true ]
do

   COUNT=$((COUNT+1))
   NEXT=`/usr/local/bin/gpio -g read 23`
   OOPS=`/usr/local/bin/gpio -g read 24`
   #success, start next
   if [ $NEXT -ge 1 ]; then
      echo "kerblam! Print was good! Let's start the next one!"
      break
   fi
   #this means it failed
   if [ $OOPS -ge 1 ]; then
      echo "kerblam! Success has kicked you in the face. The print job failed."
      echo "It will now be requeued for another shot."
      wget -O download.gcode "$printerServer?jobID=${PrintJobID:1}&stat=print"
      curl -s \
      "$printerServer" \
      -F name=$printerServer \
      -F jobID=${PrintJobID:1} \
      -F stat="print" -o download.gcode
      break
   fi
   echo "waiting...$COUNT"

   sleep 0.1
done

echo "kerblam!"
