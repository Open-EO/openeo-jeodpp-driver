#================================================
# GDAL Dockerfile for base gdal dev image
#=================================================

ARG BASE_CONTAINER 
FROM $BASE_CONTAINER as base

LABEL project="EOSSBD" \
      author="Armin Burger, Luca Marletta" \
      image_name="base_gdal_py3_deb10_dev" \
      version="4.1.0" \
      released="2020-08-26" \
      software_versions="GDAL:3.0.1  OpenJPEG:2.3.1  Python:3.7  Debian:10" \
      description="GDAL base generic image, Python 3" 
      

RUN mkdir /usr/local/lib/jeodpp  && echo "/usr/local/lib/jeodpp" > /etc/ld.so.conf.d/jeodpp.conf  &&  ldconfig

#
# Env vars for paths, library versions

ENV INSTALL_HOME=/home/install \ 
    PYTHONPATH="/usr/local/lib/python3/dist-packages" \
    GDAL_DISABLE_READDIR_ON_OPEN=TRUE \
    GDAL_VERSION="3.0.1" \
    OPENJPEG_VERSION="2.3.1" \
    OPENCV_VERSION="4.1.0" \
    PROJ4_VERSION="6.1.1" 

# Debian package installion
#
ENV DEBIAN_FRONTEND=noninteractive

# Configure apt
RUN set -xeu; \
    echo 'APT::Install-Recommends "false";' | tee -a /etc/apt/apt.conf.d/99-install-suggests-recommends; \
    echo 'APT::Install-Suggests "false";' | tee -a /etc/apt/apt.conf.d/99-install-suggests-recommends; \
    echo 'Configuring apt: OK';

COPY requirements/* /tmp/


RUN set -xeu; \ 
    apt-get update; \
    apt-get upgrade -y; \
    ## till we don't start back from base_debian10
    xargs -a /tmp/apt_0.txt apt install -yq ; \
    xargs -a /tmp/apt_1.txt apt install -yq ; \
    apt autoremove -y; \
    rm -rf /var/lib/apt/lists/*; \
    echo 'Installation of basic APT packages: OK';


FROM base as builder 

#
# Download and compile libraries
#  

# Prepare compilation directory

RUN mkdir $INSTALL_HOME

# Download
# - proj4

RUN cd $INSTALL_HOME \
    && wget -O ${PROJ4_VERSION}.tar.gz http://download.osgeo.org/proj/proj-${PROJ4_VERSION}.tar.gz \
    && tar xf ${PROJ4_VERSION}.tar.gz \
    && rm ${PROJ4_VERSION}.tar.gz

# - opencv

RUN cd $INSTALL_HOME \
    && wget -O opencv-${OPENCV_VERSION}.tar.gz https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.tar.gz \
    && tar xf opencv-${OPENCV_VERSION}.tar.gz \
    && rm opencv-${OPENCV_VERSION}.tar.gz

# - OpenJPEG

RUN cd $INSTALL_HOME \
    && wget -O openjpeg-${OPENJPEG_VERSION}.tar.gz  https://codeload.github.com/uclouvain/openjpeg/tar.gz/v${OPENJPEG_VERSION} \
    && tar xf openjpeg-${OPENJPEG_VERSION}.tar.gz \
    && rm openjpeg-${OPENJPEG_VERSION}.tar.gz

# - GDAL

RUN cd $INSTALL_HOME \
    && wget -O gdal-${GDAL_VERSION}.tar.gz http://download.osgeo.org/gdal/${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz \
    && tar xf gdal-${GDAL_VERSION}.tar.gz \
    && rm gdal-${GDAL_VERSION}.tar.gz

# Compile

RUN cd $INSTALL_HOME/proj-${PROJ4_VERSION} \
    && ./configure --disable-static \
    && make -j 10 \
    && make install \
    && make clean \
    && ldconfig

RUN cd $INSTALL_HOME/openjpeg-${OPENJPEG_VERSION} \
    && cmake . \
    && make -j 20 \
    && make install \
    && make clean \
    && ldconfig

RUN cd $INSTALL_HOME/opencv-${OPENCV_VERSION} \
    && mkdir build \
    && cd build \
    && cmake -D CMAKE_BUILD_TYPE=RELEASE \
        -D CMAKE_INSTALL_PREFIX=/usr/local \
        -D INSTALL_PYTHON_EXAMPLES=ON .. \
    && sleep 5 \
    && make -j 30 \
    && make install \
    && make clean \
    && ldconfig

RUN cd $INSTALL_HOME/gdal-${GDAL_VERSION} \
    && sed -i '304,312d' /home/install/gdal-${GDAL_VERSION}/gcore/gdaljp2abstractdataset.cpp  \
    && sed -i 's/"GDAL_DISABLE_READDIR_ON_OPEN", "NO"/"GDAL_DISABLE_READDIR_ON_OPEN", "YES"/'  \
                   /home/install/gdal-${GDAL_VERSION}/gcore/gdalopeninfo.cpp \
    && ./configure --with-pg=/usr/bin/pg_config  --with-geos=yes  --with-xerces   \
#    && ./configure --with-pg=yes  --with-geos=yes  --with-xerces  \
                   --with-python=/usr/bin/python3  --with-threads  --with-libtiff=internal  --with-geotiff=internal \
                   --with-spatialite=yes \    
                   --with-zstd=yes  --without-pam \ 
                   --with-proj=/usr/local \
    && sleep 35 \
    && make -j 30 \
    && make install  \
    && ldconfig


FROM base

ENV PYTHON_VERSION="3.7"
ARG DIST_PACKAGES="/usr/local/lib/python3.7/dist-packages"
ARG INTER_DEPLOY_MODE

COPY --from=builder    /usr/local/bin/*      /usr/local/bin/
COPY --from=builder    /usr/local/lib/*      /usr/local/lib/
COPY --from=builder    /usr/local/share/*    /usr/local/share/
COPY --from=builder    /usr/local/include/*  /usr/local/include/


#COPY --from=builder    /usr/local/lib/libmialib*    /usr/local/lib/
#COPY --from=builder    /usr/local/lib/libjiplib*    /usr/local/lib/
#COPY --from=builder    ${DIST_PACKAGES}/jiplib/*    ${DIST_PACKAGES}/jiplib/
#COPY --from=builder    ${DIST_PACKAGES}/pyjeo/*     ${DIST_PACKAGES}/pyjeo/
#COPY --from=builder    ${INSTALL_HOME}/interapro/client3deb10/inter.py                      ${DIST_PACKAGES}/jeodpp/
#COPY --from=builder    ${INSTALL_HOME}/interapro/client3deb10/lib/_inter.so                 ${DIST_PACKAGES}/jeodpp/
#COPY --from=builder    ${INSTALL_HOME}/interapro/service_files/${INTER_DEPLOY_MODE}imap/    ${DIST_PACKAGES}/jeodpp/


RUN set -xeu; \
    ldconfig


