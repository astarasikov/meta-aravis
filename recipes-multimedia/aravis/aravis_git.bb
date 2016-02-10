SUMMARY = "GStreamer support for GigE cameras"

LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=b1a8f8ba2ed964cab10244d42184a7a3"

inherit systemd

SRCREV = "8d41948020f061405ab158b4cfb63633fde62cf8"
SRC_URI = "git://git.gnome.org/aravis"

DEPENDS="gstreamer gst-plugins-base libxml2 glib-2.0 gtk-doc gobject-introspection-stub"

S = "${WORKDIR}/git"

FILES_${PN} = "${libdir}/gstreamer-0.10/*.so"
FILES_${PN} += "${bindir}/arv-*"
FILES_${PN} += "${libdir}/*.so.*"
FILES_${PN}-dbg += "${libdir}/gstreamer-0.10/.debug"
FILES_${PN}-dev += "${libdir}/gstreamer-0.10/*.la"
FILES_${PN}-staticdev += "${libdir}/gstreamer-0.10/*.a"

EXTRA_OECONF="--enable-gst-plugin-0.10 --host=${TARGET_SYS} --prefix=/usr"

do_configure_prepend() {
    ( cd ${S}
    ${S}/autogen.sh --enable-gst-plugin-0.10 --host=${TARGET_SYS} --prefix=/usr )
}

do_install () {
    oe_runmake install DESTDIR=${D}
}
