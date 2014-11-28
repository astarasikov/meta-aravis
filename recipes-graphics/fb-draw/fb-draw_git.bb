SUMMARY = "Writes patterns to the fb device"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

SRCREV = "23ac1d9e478d278646a8829def74745ea652eb53"
SRC_URI = "git://github.com/toradex/fb-draw.git;protocol=https;branch=master"

S = "${WORKDIR}/git"

do_install () {
    oe_runmake install DESTDIR=${D}
}
