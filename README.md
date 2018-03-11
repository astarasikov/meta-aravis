# What this is
This is the "layer" for building Aravis for the OpenEmbedded/Angstrom Linux distribution, alongside with the plugin for GStreamer.

[Aravis](https://github.com/AravisProject/aravis) is an open-source library for working with PointGrey cameras.
[GStreamer](https://gstreamer.freedesktop.org/) is a framework for building multimedia processing pipelines.

# Installing pre-built GStreamer binary packages:
The pre-built packages referenced in this tutorial are available at the following URL:
https://drive.google.com/drive/folders/1ZW8HGW0nQkewQoyJt5r-BXwAsdFAAWdK?usp=sharing

## Aravis
```
mkdir bin_aravis
cd bin_aravis
tar xvf ../aravis.tar.gz
opkg install deploy/ipk/armv7at2hf-neon/aravis*ipk
```

## GStreamer with WebRTC support
I have rebuilt GStreamer from OpenEmbedded with the WebRTC plugin backported from GStreamer upstream.

Some packages have unsatisfied dependencies. However, we know that in the default installation (of Angstrom LXDE image) GStreamer and most plugins work.

Therefore, if we skip all packages which have unsatisfied dependencies, we will reilstall the packages which are already installed, which is what we want.

```
mkdir bin_gst
cd bin_gst
tar xvf ../libnice.tar.gz
tar xvf ../libgst.tar.gz
tar xvf ../gstreamer.tar.gz

opkg install --force-reinstall $(find . -name '*.ipk' | grep -v webp | grep -v sbc | grep -v bad-meta | grep -v taglib | grep -v good-meta | grep -v neonhttp)  
```

# Testing Aravis in GStreamer

## Overlaying the source with GdkPixbufOverlay
We can overlay the video feed with an arbitrary PNG image using `gdkpixbufoverlay`.

```
gst-launch-1.0 -v aravissrc ! videoconvert !  gdkpixbufoverlay location=crosshair.png ! theoraenc ! oggmux ! filesink location=test.ogg
```

## Encoding Camera stream to H.264 with NVIDIA HW-accelerated encoder
```
gst-launch-1.0 -v aravissrc ! nvvidconv ! omxh264enc ! qtmux ! filesink location=test.mp4
```

# Testing HLS streaming
Example scripts described below are also available inside this repository in the [demos/hls](demos/hls) folder.

## Creating the folders
This tutorial assumes you create the folder named `/home/root/builds/hls` and put the scripts there.
To improve performance and reduce wearing to the eMMC storage, consider using the `tmpfs` virtual filesystem in RAM.

```
mkdir -p /home/root/builds/hls
mount -t tmpfs none /home/root/builds/hls
```

## Sample M3U8 playlist for HLS
We also need a sample playlist file (M3U8) for the client (browser). GStreamer will generate one and update it dynamically, but here is an example in case you need one for testing. Put it to `/home/root/builds/hls/output.m3u8`.

```
#EXTM3U
#EXT-X-TARGETDURATION:10
#EXT-X-VERSION:3
#EXT-X-MEDIA-SEQUENCE:1
#EXTINF:10,
segment1.ts
#EXTINF:10,
segment2.ts
#EXTINF:10,
segment3.ts
#EXTINF:10,
segment4.ts
#EXTINF:10,
segment5.ts
```

## HTML file
We need an HTML file to tell the browser where to obtain the video feed from. Additionally, we need to use a client-side JavaScript library to handle HLS.

Place the following HTML file into the root of your web server (for this example, `/home/root/builds/hls/test_js_hls.html`).

```html
<html>
<body>

<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<video id="video"></video>
<script>
  if(Hls.isSupported()) {
    var video = document.getElementById('video');
    var hls = new Hls();
    hls.loadSource('http://127.0.0.0:8000/output.m3u8');
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED,function() {
      video.play();
  });
 }
</script>
</body>
```

## Simple HTTP Server
We need an HTTP server. The way HLS streaming works is that the encoder (GStreamer pipeline) writes chunks of video (MPEG Transport Stream) into a folder, and the client fetches them over HTTP.

For a start, we can use the SimpleHTTPServer from Python2 (or http.server from Python3).

First, we need to install Python.
```
opkg update
opkg install python3

# or install Python 2.X
# opkg install python
```

Now we can launch the HTTP server.
```
cd /home/root/builds/hls/
python3 -m http.server 8000

# or python2 -m SimpleHTTPServer 8000
```

## Launching the encoder pipeline

### Test Feed
First, ensure that the encoder and HLS pipeline are working. For that, use the "videotestsrc" GStreamer element.
```
gst-launch-1.0 -v videotestsrc is-live=true ! omxh264enc ! mpegtsmux ! hlssink target-duration=1 max-files=5 location=/home/root/builds/hls/segment%d.ts playlist-location=/home/root/builds/hls/output.m3u8 playlist-root=http://127.0.0.0:8000/
```

### Testing the Aravis camera
Now we can launch the video from the Aravis camera and overlay a test PNG image.
```
gst-launch-1.0 -v aravissrc ! gdkpixbufoverlay offset-x=300 offset-y=500 location=/usr/share/icons/nuoveXT2/128x128/devices/computer.png ! nvvidconv  ! omxh264enc ! mpegtsmux ! hlssink target-duration=1 max-files=5 location=/home/root/builds/hls/segment%d.ts playlist-location=/home/root/builds/hls/output.m3u8 playlist-root=http://127.0.0.1:8000/
```

## Viewing the feed remotely
Normally you would replace "127.0.0.1" with the address of your Apalis board on your network. Sometimes it is not possible. For example, when you have SSH access to the board for testing but your PC is not on the same network.

Set up SSH tunnel so that TCP connections to port 8000 locally get forwarded to port 8000 on the Apalis board.
```
ssh -L 8000:localhost:8000 root@WOW_SO_VERY_HOST -p7777
```

Open the URL from the web browser on your PC.
```
http://127.0.0.1:8000/test_js_hls.html
```

## Fixing NVIDIA libraries
At some poing after running `opkg update` and `opkg install python` I have noticed that NVIDIA pluging for GStreamer stopped working. I think the problem is that for Apalis, the OpenEmbedded overlay is not added and `/etc/opkg/apalis_tk1-feed.conf` is empty.

If you run into this problem for some reason, re-install the NVIDIA IPKs (which you can get from the `deploy` folder after you build OpenEmbedded) and add the dynamic libraries search path to `/etc/ld.so.conf`.

```
cat > /etc/ld.so.conf <<EOF
/usr/lib/arm-linux-gnueabihf/tegra
/usr/lib/arm-linux-gnueabihf/tegra-egl
EOF

ldconfig
```

### installing NVIDIA packages
```
mkdir bin_nvidia
cd bin_nvidia
tar xvf ../nvidia.tar.bz2
opkg install --force-reinstall $(find . -name *.ipk | grep -v kernel)
```

# Building Aravis for Toradex Apalis TK1
The overall build process is documented on Toradex wiki.
The only difference is adding our custom layer "meta-aravis".

* Toradex Wiki: https://developer.toradex.com/knowledge-base/board-support-package/openembedded-(core)
* OpenEmbedded Wiki: http://www.openembedded.org/wiki/Getting_started#Required_software

In addition to the software listed on the OpenEmbedded Wiki, I
had to install the following:
```
g++-multilib
```

First, we need to clone the manifest using the `repo` tool.
```
# First, install any version of repo from Google
mkdir -p ~/bin/
export PATH=~/bin:$PATH

# Now, sync the manifest and use the local repo binary
~/bin/repo init -u http://git.toradex.com/toradex-bsp-platform.git -b LinuxImageV2.8
cp /mnt/oe/oe_tegra/.repo/repo/repo ~/bin/repo
repo sync
```

Now we need to edit `conf/local.conf` and select the board for which we're building Angstrom.
```
vim build/conf/local.conf
# uncomment the line starting with MACHINE and set it to "apalis-tk1":
# MACHINE ?= "apalis-tk1"

. export
bitbake -k angstrom-lxde-image
```

Now we need to add the layer for aravis (this repository).
```
cd layers/
git clone https://github.com/astarasikov/meta-aravis.git
cd ..
```

Now, edit `bblayers.conf` to add the "meta-aravis" layer to the list of layers so that OpenEmbedded build system (bitbake) can see the new package.
```
vim build/conf/bblayers.conf
# add "${TOPDIR}/../layers/meta-aravis \"
# similar to how other layers are defined
bitbake -k aravis
```

# TODO WebRTC
Recently the WebRTC plugin was integrated to GStreamer upstream. It shall be availabe in GStreamer starting with version **1.14**.
Current version of GStreamer in Angstrom/OpenEmbedded is **1.12.1**.

Updating GStreamer is quite challenging, especially on a Tegra-based board where proprietary plugins are used for controlling hardware encoders (because of ABI compatibility).

I have backported the WebRTC plugin from **1.14** to **1.12.1**.
I did not have time to set up the full WebRTC pipeline yet. It needs an additional signalling server, and also additional GStreamer functionality might need backporting (such as changes to the DTLS plugin).

The patches to GSTreamer **1.12.1** are available below. It also lists the changes you need to make to the local copy of the OpenEmbedded layers for GStreamer.
https://gist.github.com/astarasikov/0f7a9854befd93c8ff4b742fd3760449
