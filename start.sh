#!/bin/bash

cvlc \
  --intf=http \
  --http-port=9090 \
  --http-password=1234 \
  --width=640 \
  --height=480 \
  --no-osd \
  --no-xlib \
  --loop \
  --random \
  videos