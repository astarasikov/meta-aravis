SUMMARY = "Writes patterns to the fb device"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

inherit systemd

SRCREV = "23ac1d9e478d278646a8829def74745ea652eb53"
SRC_URI = "git://github.com/toradex/fb-draw.git;protocol=https;branch=master"
SRC_URI += "file://fb-draw.service"

S = "${WORKDIR}/git"

do_install () {
    oe_runmake install DESTDIR=${D}

    install -d ${D}${systemd_unitdir}/system/ ${D}${sysconfdir}/systemd/system/
    install -m 0644 ${WORKDIR}/fb-draw.service ${D}${systemd_unitdir}/system
    ln -s /dev/null ${D}${sysconfdir}/systemd/system/getty@tty1.service
}

NATIVE_SYSTEMD_SUPPORT = "1"
SYSTEMD_PACKAGES = "${PN}"
SYSTEMD_SERVICE_${PN} = "fb-draw.service"
