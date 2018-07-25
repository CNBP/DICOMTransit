#!/bin/sh

#Bash command to read in the files.

#Generate Heuristic Files

docker run --rm -it \
#Volume Mounting
-v ~/:/data:ro \
#Volume Mounting
-v ~/BIDS:/output \

nipy/heudiconv:latest
-d /data/{subject}/{session}/SCANS/*/DICOM/*.dcm \  #This is the input data structure!
-#!/bin/sh
-s SUBJECT_ID \
--ses SESSION_ID \

-f convertall \
-c none \
-o /output

# run with edited heuristic file
