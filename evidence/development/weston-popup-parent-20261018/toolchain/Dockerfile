FROM avelino-toolchain:recovered-weston13-cjk-v1-20261018-qt6.8.3
COPY tools/install-weston.sh tools/weston-popup-parent.patch tools/weston-popup-order.c tools/check-weston-popup-parent.sh /usr/local/lib/avelino/
COPY weston-13.0.4.tar.xz /tmp/weston-source.tar.xz
RUN AVELINO_WESTON_ARCHIVE=/tmp/weston-source.tar.xz bash /usr/local/lib/avelino/install-weston.sh && rm /tmp/weston-source.tar.xz
RUN bash /usr/local/lib/avelino/check-weston-popup-parent.sh /opt/weston-13.0.4/share/avelino/popup-parent-regression
