wget http://download.videolan.org/vlc/2.2.5.1/vlc-2.2.5.1.tar.xz
tar -xJf vlc-2.2.5.1.tar.xz

apt-get update

sudo apt-get install autopoint gettext liba52-0.7.4-dev libaa1-dev libasound2-dev libass-dev libavahi-client-dev libavc1394-dev libavcodec-dev libavformat-dev libbluray-dev libcaca-dev libcddb2-dev libcdio-dev libchromaprint-dev libdbus-1-dev libdc1394-22-dev libdca-dev libdirectfb-dev libdvbpsi-dev libdvdnav-dev libdvdread-dev libegl1-mesa-dev libfaad-dev libflac-dev libfluidsynth-dev libfreerdp-dev libfreetype6-dev libfribidi-dev libgl1-mesa-dev libgles1-mesa-dev libgles2-mesa-dev libgnutls28-dev libgtk2.0-dev libidn11-dev libiso9660-dev libjack-jackd2-dev libkate-dev liblircclient-dev liblivemedia-dev liblua5.2-dev libmad0-dev libmatroska-dev libmodplug-dev libmpcdec-dev libmpeg2-4-dev libmtp-dev libncursesw5-dev libnotify-dev libogg-dev libomxil-bellagio-dev libopus-dev libpng12-dev libpulse-dev libqt4-dev libraw1394-dev libresid-builder-dev librsvg2-dev libsamplerate0-dev libschroedinger-dev libsdl-image1.2-dev libsdl1.2-dev libshine-dev libshout3-dev libsidplay2-dev libsmbclient-dev libspeex-dev libspeexdsp-dev libssh2-1-dev libswscale-dev libtag1-dev libtheora-dev libtwolame-dev libudev-dev libupnp-dev libv4l-dev libva-dev libvcdinfo-dev libvdpau-dev libvncserver-dev libvorbis-dev libx11-dev libx264-dev libxcb-composite0-dev libxcb-keysyms1-dev libxcb-randr0-dev libxcb-shm0-dev libxcb-xv0-dev libxcb1-dev libxext-dev libxinerama-dev libxml2-dev libxpm-dev libzvbi-dev lua5.2 oss4-dev pkg-config zlib1g-dev libtool build-essential autoconf
cd vlc-2.2.5.1

./bootstrap

CFLAGS="-I/opt/vc/include/ -I/opt/vc/include/interface/vcos/pthreads -I/opt/vc/include/interface/vmcs_host/linux -I/opt/vc/include/interface/mmal -I/opt/vc/include/interface/vchiq_arm -I/opt/vc/include/IL -I/opt/vc/include/GLES2 -mfloat-abi=hard -mcpu=cortex-a7 -mfpu=neon-vfpv4" CXXFLAGS="-I/opt/vc/include/ -I/opt/vc/include/interface/vcos/pthreads -I/opt/vc/include/interface/vmcs_host/linux -I/opt/vc/include/interface/mmal -I/opt/vc/include/interface/vchiq_arm -I/opt/vc/include/IL -mfloat-abi=hard -I/opt/vc/include/GLES2 -mcpu=cortex-a7 -mfpu=neon-vfpv4" LDFLAGS="-L/opt/vc/lib" ./configure --prefix=/usr --enable-omxil --enable-omxil-vout --enable-rpi-omxil --disable-mmal-codec --disable-mmal-vout --enable-gles2

make -j3

make install