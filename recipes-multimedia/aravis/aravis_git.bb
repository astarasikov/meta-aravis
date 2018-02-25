SUMMARY = "GStreamer support for GigE cameras"

LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=b1a8f8ba2ed964cab10244d42184a7a3"

inherit systemd

SRC_URI = "https://github.com/AravisProject/aravis/archive/ARAVIS_0_5_11.tar.gz"
SRC_URI[md5sum] = "af1445f4709cbc778c3736b3a58ae821"

SRC_URI += " \
	file://aravis-disable-gtkdoc.patch \
"

DEPENDS=" \
	gstreamer1.0 \
	gstreamer1.0-plugins-base \
	libxml2 \
	glib-2.0 \
	glib-2.0-native \
	gtk-doc \
	gobject-introspection \
	intltool-native \
"

S = "${WORKDIR}/aravis-ARAVIS_0_5_11"

FILES_${PN} = "${libdir}/gstreamer-1.0/*.so"
FILES_${PN} += "${bindir}/arv-*"
FILES_${PN} += "${libdir}/*.so.*"
FILES_${PN}-dbg += "${libdir}/gstreamer-1.0/.debug"
FILES_${PN}-dev += "${libdir}/gstreamer-1.0/*.la"
FILES_${PN}-staticdev += "${libdir}/gstreamer-1.0/*.a"

EXTRA_OECONF="--enable-gst-plugin --enable-introspection=no --enable-gtk-doc=no --host=${TARGET_SYS} --prefix=${prefix}"

do_configure_prepend() {
    ( cd ${S}
    ${S}/autogen.sh --enable-gst-plugin --enable-introspection=no --enable-gtk-doc=no --host=${TARGET_SYS} --prefix=${prefix} )
}

do_install () {
    oe_runmake install DESTDIR=${D}
}
