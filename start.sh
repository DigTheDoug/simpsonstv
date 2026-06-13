#!/bin/bash

# --avcodec-hw=none - turns off hardware encoding.
#   - Used  on the Pi Zero OS v11 to keep the video from showing just green after a long play period. 
#   - Removed from OS v12 larger screen version, when in place videos have trouble decoding, especially larger videos
# --no-xlib
#    - Used on the Pi Zero OS v11 to allow playback
#    - Removed from OSv12 larger screen version, when in place all you see is green screen.
# --width,height
#    - change to whichever screen you are using

cvlc \
  --intf=http \
  --http-port=9090 \
  --http-password=1234 \
  --width=640 \
  --height=480 \
  --no-qt-video-autoresize \
  --no-osd \
  --loop \
  --random \
  videos