FROM avelino-toolchain:recovered-a11y-20261017-qt6.8.3
COPY install-weston.sh /usr/local/lib/avelino/install-weston.sh
RUN bash /usr/local/lib/avelino/install-weston.sh
ENV PATH=/opt/weston-13.0.4/bin:$PATH
ENV LD_LIBRARY_PATH=/opt/weston-13.0.4/lib:/opt/qt/lib
RUN weston --version && qmake -query QT_VERSION
