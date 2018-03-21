#!/usr/bin/env python3

# Example Usage:
# ./http_remote.py 'aravissrc blocksize=400000 ! capsfilter caps="video/x-raw, format=UYVY, width=(int)1024, height=(int)1024" ! timeoverlay ! gdkpixbufoverlay name=test_overlay offset-x=300 offset-y=500 location=/usr/share/icons/nuoveXT2/128x128/devices/computer.png ! nvvidconv  ! omxh264enc low-latency=true profile=1 control-rate=1 quality-level=0 iframeinterval=60 bitrate=8000000 insert-sps-pps=true ! h264parse ! mpegtsmux ! tcpserversink host=127.0.0.1 port=8000'
# ./http_remote.py 'aravissrc blocksize=400000 ! capsfilter caps="video/x-raw, format=UYVY, width=(int)1024, height=(int)1024" ! timeoverlay ! gdkpixbufoverlay name=test_overlay offset-x=300 offset-y=500 location=/usr/share/icons/nuoveXT2/128x128/devices/computer.png ! nvvidconv  ! omxh264enc low-latency=true profile=1 control-rate=1 quality-level=0 iframeinterval=60 bitrate=8000000 insert-sps-pps=true ! h264parse ! mpegtsmux ! hlssink target-duration=1 max-files=10 location=/home/root/builds/hls/segment%d.ts playlist-location=/home/root/builds/hls/output.m3u8 playlist-root=http://127.0.0.1:8000/ '

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib, GObject

from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import _thread
import threading

import sys

ARAVIS_PIPELINE="\
aravissrc blocksize=400000 !\
 capsfilter caps=\"video/x-raw, format=UYVY, width=(int)1024, height=(int)1024\" !\
 timeoverlay !\
 gdkpixbufoverlay name=test_overlay offset-x=300 offset-y=500 location=/usr/share/icons/nuoveXT2/128x128/devices/computer.png !\
 nvvidconv  !\
 omxh264enc low-latency=true profile=1 control-rate=1 quality-level=0 iframeinterval=60 bitrate=8000000 insert-sps-pps=true !\
 h264parse !\
 mpegtsmux !\
 hlssink target-duration=1 max-files=10 location=/home/root/builds/hls/segment%d.ts playlist-location=/home/root/builds/hls/output.m3u8 playlist-root=http://127.0.0.1:8000/ \
"

# tcpserversink host=127.0.0.1 port=8001\


###############################################################################
# Global Variables
###############################################################################
g_overlay_params = None
g_http_lock = threading.Lock()

HTTP_PORT_CONTROL = 8000
###############################################################################
# Wrapper class for GStreamer pipeline
###############################################################################
class CustomPipeline:
    def __init__(self, pipeline_string):
        self.pipeline = Gst.parse_launch(pipeline_string)
        self.overlay = self.pipeline.get_by_name("test_overlay")
        #bus = self.pipeline.get_bus()
        #bus.add_signal_watch()
        #bus.connect("message", self.on_message)

    def start(self):
        GLib.timeout_add(50, self.idle_handler)
        self.pipeline.set_state(Gst.State.PLAYING)

    def idle_handler(self):
        global g_overlay_params
        global g_http_lock

        if not g_http_lock.acquire(blocking=False):
            return 1

        overlay_params = g_overlay_params
        g_overlay_params = None
        g_http_lock.release()

        if not overlay_params:
            return 1

        print("update was requested via HTTP")
        self.overlay.set_property("offset-x", overlay_params['offset-x'])
        self.overlay.set_property("offset-y", overlay_params['offset-y'])
        return 1

    def on_message(self, bus, message):
        print(message)

###############################################################################
# HTTP request handler for controlling the overlay parameters
###############################################################################
class HttpControlHandler(SimpleHTTPRequestHandler):
    def parse_overlay_params(self):
        try:
            if not self.path.startswith("/update"):
                raise AttributeError("Path is not /update")

            parsed_args = urlparse(self.path)
            query_args = parse_qs(parsed_args.query)
            print("Args: self.path=%s path=%s offset_x=%s offset_y=%s" % (self.path, parsed_args.path, query_args["offset_x"], query_args["offset_y"]))

            # Create the dictionary with the parsed values for the parameters.
            # If a parameter was not present, KeyError or AttributeError is thrown
            # If parameter fails to parse as int, ValueError is thrown
            # If parameter is specified but value is not, IndexError is thrown
            new_params = {
                    'offset-x' : int(query_args["offset_x"][0]),
                    'offset-y' : int(query_args["offset_y"][0]),
            }
            return new_params
        except (KeyError, AttributeError, ValueError, IndexError):
            return None

    def publish_overlay_params(self, new_params):
        if not new_params:
            return
        global g_overlay_params
        global g_http_lock
        g_http_lock.acquire()
        g_overlay_params = new_params
        g_http_lock.release()

    def do_GET(self):
        print("HTTP GET")
        new_params = self.parse_overlay_params()
        if new_params:
            self.publish_overlay_params(new_params)
            self.send_response(200)
            self.end_headers()
        else:
            SimpleHTTPRequestHandler.do_GET(self)

###############################################################################
# Routine for running the HTTP control server in a separate thread
###############################################################################
def HttpControlThreadEntry():
    try:
        server = HTTPServer(('127.0.0.1', HTTP_PORT_CONTROL), HttpControlHandler)
        server.serve_forever()
    except:
        print("server error")
        server.socket.close()

###############################################################################
# Entry Point
###############################################################################
if __name__ == "__main__":
    pipeline_string = ARAVIS_PIPELINE
    param_string = ' '.join(sys.argv[1:])
    if len(param_string) > 0:
        pipeline_string = param_string

    GObject.threads_init()
    Gst.init(None)
    loop = GLib.MainLoop()

    pipeline_obj = CustomPipeline(pipeline_string)
    pipeline_obj.start()

    #pipeline = Gst.parse_launch("videotestsrc ! fakesink")
    #pipeline.set_state(Gst.State.PLAYING)

    _thread.start_new_thread(HttpControlThreadEntry, ())
    loop.run()


