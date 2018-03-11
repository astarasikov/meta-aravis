#!/bin/bash

gst-launch-1.0 -v videotestsrc is-live=true !\
 'video/x-raw, format=(string)I420, width=(int)1280, height=(int)720' !\
 timeoverlay !\
 gdkpixbufoverlay offset-x=300 offset-y=500 location=/usr/share/icons/nuoveXT2/128x128/devices/computer.png !\
 nvvidconv  !\
 omxh264enc profile=2 control-rate=4 quality-level=1 iframeinterval=10 !\
 mpegtsmux !\
 hlssink target-duration=1 max-files=5 location=/home/root/builds/hls/segment%d.ts playlist-location=/home/root/builds/hls/output.m3u8 playlist-root=http://127.0.0.1:8000/
