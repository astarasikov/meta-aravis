#!/bin/bash

gst-launch-1.0 -v videotestsrc is-live=true ! omxh264enc ! mpegtsmux ! hlssink target-duration=1 max-files=5 location=/home/root/builds/hls/segment%d.ts playlist-location=/home/root/builds/hls/output.m3u8 playlist-root=http://127.0.0.1:8000/
