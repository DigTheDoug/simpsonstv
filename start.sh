#!/bin/bash

# avcodec-hw=none - turns off hardware encoding. Used on the Pi Zero to keep the video from showing just green after a long play period

cvlc \
  --intf=http \
  --http-port=9090 \
  --http-password=1234 \
  --width=640 \
  --height=480 \
  --avcodec-hw=none \
  --no-osd \
  --no-xlib \
  --loop \
  --random \
  videos