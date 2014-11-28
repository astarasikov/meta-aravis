SUMMARY = "A console-image for our fb-test product."

IMAGE_FEATURES += "ssh-server-openssh"
IMAGE_INSTALL += "fb-draw"
IMAGE_INSTALL += "connman connman-systemd connman-plugin-loopback connman-plugin-ethernet"

LICENSE = "MIT"

#create the deployment directory-tree
PV = "V1.0"
IMAGE_NAME = "${MACHINE}_product"
require recipes/images/trdx-image-fstype.inc

inherit core-image
