#!/bin/bash

rm ./segment*.ts

gst-launch-1.0 -v aravissrc blocksize=400000 !\
 'video/x-raw, format=UYVY, width=(int)1024, height=(int)1024' !\
 nvvidconv  !\
 omxh264enc low-latency=true profile=1 control-rate=2 quality-level=0 iframeinterval=20 bitrate=8000000 !\
 mpegtsmux !\
 hlssink target-duration=1 max-files=10 location=/home/root/builds/hls/segment%d.ts playlist-location=/home/root/builds/hls/output.m3u8 playlist-root=http://127.0.0.1:8000/
