# syntax=docker/dockerfile:1.1.7-experimental
ARG BASE_CONTAINER 
FROM $BASE_CONTAINER as jeodpp_base

LABEL project="EOSSBD" \
      author="Luca Marletta" \
      image_name="jeodpp_base_gdal_py3_deb10_jeolib_openeo" \
      version="0.1.0" \
      released="2020-08-26" \
      software_versions="Code from Gitlab up to date" \
      description="Compiled code get directly from gitlab repository plus jupyterlab" 
      
#
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
    xargs -a /tmp/apt_1.txt apt install -yq ; \
    apt autoremove -y; \
    #rm -rf /var/lib/apt/lists/*; \
    echo 'Installation of basic APT packages: OK';

# Install basic packages
RUN set -xeu; \
    #apt update; \
    apt install -yq \
        bsdtar \
        bzip2 \
        ca-certificates \
        curl \
        file \
        git \
        gosu \
        gzip \
        jq \
        moreutils \
        procps \
        silversearcher-ag \
        tar \
        tree \
        unzip \
        vim \
        less \
        wget \
        zip \
        libgeotiff-dev \
        libgsl0-dev \
        libfann-dev \
        libfftw3-dev \
        libshp-dev \
        doxygen \
        python-epydoc \
        #texlive \
        latex2html \
        uthash-dev \
        libjsoncpp-dev \
        libboost-serialization-dev \
        libboost-filesystem-dev \
        python3-setuptools \
        curl \
        libtool; \
    rm -rf /var/lib/apt/lists/* ;


ENV PYTHON_VERSION="3.7"
ARG PATH=/usr/local/bin:$PATH


ARG LD_LIBRARY_PATH=/usr/local/include:/usr/local/include/gdal:/usr/local/lib:/usr/lib/:/usr/include/python${PYTHON_VERSION}m/:$LD_LIBRARY_PATH
ARG DIST_PACKAGES="/usr/local/lib/python${PYTHON_VERSION}/dist-packages"
ARG PYTHONPATH=${DIST_PACKAGES}:/usr/lib/python${PYTHON_VERSION}/dist-packages

ENV PYTHONPATH=$PYTHONPATH
ENV DIST_PACKAGES=${DIST_PACKAGES}



FROM jeodpp_base AS builder

# Ensure that the mandatory build arguments have been provided
ARG MIALIB_HASH
ARG JIPLIB_HASH
ARG PYJEO_HASH
ARG JEOLIBRARIES_HASH
ARG OPENEO_HASH
ARG INTER_HASH

ARG INTER_DEPLOY_MODE

LABEL org.jeodpp.software.version.mialib=${MIALIB_HASH}
LABEL org.jeodpp.software.version.jiplib=${JIPLIB_HASH}
LABEL org.jeodpp.software.version.inter=${PYJEO_HASH}
LABEL org.jeodpp.software.version.jeo_libraries=${JEOLIBRARIES_HASH}
LABEL org.jeodpp.software.version.openeo=${OPENEO_HASH}
LABEL org.jeodpp.software.version.inter=${INTER_HASH}

#
# Download and compile libraries
#  

# Env vars for paths, library versions
ENV INSTALL_HOME=/home/install

RUN mkdir -p $INSTALL_HOME

ARG GITLAB_TOKEN

RUN curl --header "PRIVATE-TOKEN:$GITLAB_TOKEN" \
         --output $INSTALL_HOME/mia.tar.gz \
         https://jeodpp.jrc.ec.europa.eu/apps/gitlab/api/v4/projects/jeodpp%2FJIPlib%2Fmia/repository/archive.tar.gz${MIALIB_HASH} \
         --verbose ;


# - mia
RUN set -xeu; \
    PYVER=$(python3 --version|sed 's/Python \(3.[0-9]\).[0-9]/\1/');\
    cd $INSTALL_HOME;\
    tar xzvf mia.tar.gz ; \
    cd $INSTALL_HOME/mia-* ; \
    sed -i "s/PYVER = 3.6/PYVER = ${PYVER}/" Makefile ; \
    sed -i "s/PYVER=3.6/PYVER=${PYVER}/" core/c/Makefile ; \
    sed -i "s/PYVER = 3.6/PYVER = ${PYVER}/" core/c/Makefile ; \ 
    sed -i "s/PYVER .*= 3.6/PYVER = ${PYVER}/" swig/python/Makefile ; \
    make build ; \
    make install ; \
    ldconfig ; \
    cd $INSTALL_HOME ; \
    rm mia.tar.gz;  \
    rm -rf $INSTALL_HOME/mia-* ;

RUN echo "UPDATE JIPLI B" ;

RUN curl --header "PRIVATE-TOKEN:$GITLAB_TOKEN" \
         --output $INSTALL_HOME/jiplib.tar.gz \
         https://jeodpp.jrc.ec.europa.eu/apps/gitlab/api/v4/projects/jeodpp%2FJIPlib%2Fjiplib/repository/archive.tar.gz${JIPLIB_HASH} \
         --verbose ;

# - jiplib
RUN set -xeu ; \
    cd $INSTALL_HOME ; \
    tar xzvf jiplib.tar.gz ; \
    cd $INSTALL_HOME/jiplib-* ; \
    mkdir build ; \
    cd build ; \
    cmake .. ; \
    sleep 5 ; \
    make -j 30 ; \
    make install ; \
    ldconfig ; \
    cd $INSTALL_HOME ; \
    rm jiplib.tar.gz ;

RUN echo "download pyjeo"

RUN curl --header "PRIVATE-TOKEN:$GITLAB_TOKEN" \
         --output $INSTALL_HOME/pyjeo.tar.gz \
         https://jeodpp.jrc.ec.europa.eu/apps/gitlab/api/v4/projects/jeodpp%2FJIPlib%2FpyJEO/repository/archive.tar.gz${PYJEO_HASH} \
         --verbose

# - pyjeo
RUN cd $INSTALL_HOME \
    && tar xzvf pyjeo.tar.gz \
    && cd $INSTALL_HOME/pyJEO-* \
    && python3 setup.py install \
    && cd $INSTALL_HOME \
    && rm pyjeo.tar.gz


RUN echo "UPDATE THE LATEST JEO-LIBRARIES"

RUN curl --header "PRIVATE-TOKEN:$GITLAB_TOKEN" \
         --output $INSTALL_HOME/jeo-libraries.tar.gz \
         https://jeodpp.jrc.ec.europa.eu/apps/gitlab/api/v4/projects/jeodpp-services%2Fjeo-libraries/repository/archive.tar.gz${JEOLIBRARIES_HASH} \
         --verbose

# - jeo-libraries
RUN cd $INSTALL_HOME \
    && tar xzvf jeo-libraries.tar.gz \
    && cd $INSTALL_HOME/jeo-libraries-* \
    && python3 setup.py install \
    && cd $INSTALL_HOME \
    && rm jeo-libraries.tar.gz

RUN echo "UPDATE OPENEO PYTHON GRAPH PARSER"

RUN cd $INSTALL_HOME \
    && git clone https://github.com/Open-EO/openeo-pg-parser-python.git \
    && cd openeo-pg-parser-python \
    && python3 setup.py install \
    && cd $INSTALL_HOME \
    && rm -rf openeo-pg-parser-python

RUN echo "UPDATE openeo backend v4"

RUN curl --header "PRIVATE-TOKEN:$GITLAB_TOKEN" \
         --output $INSTALL_HOME/openeo-jeodpp-backend.tar.gz \
         https://jeodpp.jrc.ec.europa.eu/apps/gitlab/api/v4/projects/jeodpp%2FopenEO/repository/archive.tar.gz${OPENEO_HASH} \
         --verbose ;

RUN cd $INSTALL_HOME \
    && tar xzvf openeo-jeodpp-backend.tar.gz \
    && cd $INSTALL_HOME/openeo-master-* \
    && cd back_end \
    && python3 setup.py install \
    && cd $INSTALL_HOME \
    && rm openeo-jeodpp-backend.tar.gz \
    && rm -rf openeo-master-*


# Download and compile INTERAPRO

# Before we compile we need to edit jmorecfg. We need root for this!
# For more info check:
# https://jeodpp.jrc.ec.europa.eu/apps/gitlab/jeodpp/interapro/interapro/issues/3

RUN set -xeu; \
#    sed -i "s/typedef long INT32/typedef int INT32/" /usr/local/include/jmorecfg.h; \
    sed -i "s/typedef long INT32/typedef int INT32/" /usr/include/jmorecfg.h; \
    echo 'patch libjpeg: OK';

#RUN --mount=type=secret,mode=0444,id=gitlab_token,required=true \
RUN set -xeu; \
    curl --header "PRIVATE-TOKEN:$GITLAB_TOKEN" \
         --output $INSTALL_HOME/interapro.tar.gz \
         https://jeodpp.jrc.ec.europa.eu/apps/gitlab/api/v4/projects/jeodpp%2Finterapro%2Finterapro/repository/archive.tar.gz${INTER_HASH} \
         --verbose; \
    echo 'donwload interapro: OK'; \
    # unpack and remove the tar
    cd "${INSTALL_HOME}"; \
    tar -xf interapro.tar.gz; \
    mv ./interapro-* interapro; \
    echo 'ok';

ENV PYTHON_BIN='python3'
 
RUN set -xeu; \
    cd "${INSTALL_HOME}"/interapro; \
    # compile
    cd hiredis-0.13.3; \
    # only use the 2/3 of available CPUs
    nice make -j $((2 * $(nproc) / 3)); \
    cd ../; \
    # In this Dockerfile, we use GDAL from the repos.
    # In the old ones we compile GDAL from source into /usr/local/include
    # This means that in order to compile interapro we need to add
    # `/usr/include/gdal` in the included directories
    sed -e 's;CLIENTINCLUDE    = ;CLIENTINCLUDE    = -I/usr/local/include/gdal -I/usr/include/python3.7m ;' \
        -e 's;SERVERINCLUDE    = ;SERVERINCLUDE    = -I/usr/local/include/gdal -I/usr/include/python3.7m ;' \
        -i makefile; \
    # only use the 2/3 of available CPUs
    nice make -j $((2 * $(nproc) / 3)) client;


RUN ls -l /usr/local/lib/ /usr/local/lib/python3.7/dist-packages

FROM jeodpp_base

LABEL org.jeodpp.software.version.mialib=${MIALIB_HASH}
LABEL org.jeodpp.software.version.jiplib=${JIPLIB_HASH}
LABEL org.jeodpp.software.version.inter=${PYJEO_HASH}
LABEL org.jeodpp.software.version.jeo_libraries=${JEOLIBRARIES_HASH}
LABEL org.jeodpp.software.version.openeo=${OPENEO_HASH}
LABEL org.jeodpp.software.version.inter=${INTER_HASH}


ARG DIST_PACKAGES="/usr/local/lib/python3.7/dist-packages"
ENV INSTALL_HOME="/home/install"
ARG INTER_DEPLOY_MODE

COPY --from=builder    /usr/local/bin/*     /usr/local/bin/
COPY --from=builder    /usr/local/lib/*     /usr/local/lib/
COPY --from=builder    /usr/local/share/*   /usr/local/share/
COPY --from=builder    /usr/local/include/* /usr/local/include/


#COPY --from=builder    /usr/local/lib/libmialib*    /usr/local/lib/
#COPY --from=builder    /usr/local/lib/libjiplib*    /usr/local/lib/
COPY --from=builder    ${DIST_PACKAGES}/*           ${DIST_PACKAGES}/
#COPY --from=builder    ${DIST_PACKAGES}/jiplib/*    ${DIST_PACKAGES}/jiplib/
#COPY --from=builder    ${DIST_PACKAGES}/pyjeo*/*     ${DIST_PACKAGES}/pyjeo/
COPY --from=builder    ${INSTALL_HOME}/interapro/client3deb10/inter.py                      ${DIST_PACKAGES}/jeodpp/
COPY --from=builder    ${INSTALL_HOME}/interapro/client3deb10/lib/_inter.so                 ${DIST_PACKAGES}/jeodpp/
COPY --from=builder    ${INSTALL_HOME}/interapro/service_files/${INTER_DEPLOY_MODE}/imap/   ${DIST_PACKAGES}/jeodpp/




## Setting for Jupyterlab

ARG USER="jovyan"
ARG USER_ID="1000"
ARG NB_GID="100"

ENV NB_USER=$USER
ENV NB_UID=$USER_ID
ENV SHELL=/bin/bash 
ENV HOME=/home/$NB_USER

ENV JUPYTERHUB_VERSION='1.1.*'
ENV JUPYTERLAB_VERSION='2.1.3'
ENV NOTEBOOK_VERSION='6.0.3'

COPY requirements/* /tmp/

#RUN set -xeu; \ 
#    apt-get update; \
#    xargs -a /tmp/apt_2.txt apt install -yq ; \
#    apt autoremove -y; \
#    rm -rf /var/lib/apt/lists/*; 


RUN set -xeu; \ 
    # Add the user
    useradd -u ${USER_ID} -m -s /bin/bash ${NB_USER}; \
    usermod -a -G users ${NB_USER}; \
    mkdir -p /home/$NB_USER/work; \
    chown -R $USER_ID:$NB_GID /home/$NB_USER ; \
    echo "Creating user ${NB_USER}: OK";


RUN printf "PATH:$PATH \nPYTHONPATH $PYTHONPATH\n"


# Install nodejs and pip packages
RUN set -xeu; \
    curl -sL https://deb.nodesource.com/setup_12.x | bash - ; \
    apt update; \
    apt install -yq build-essential nodejs; \
    pip3 install --upgrade pip setuptools; \
    pip3 install --no-compile --no-cache `/tmp/parser.sh /tmp/pip_1.txt`; \
    apt autoremove --purge -yq; \
    rm -rf /var/lib/apt/lists/*; \
    echo 'install requirements: OK'


RUN set -xeu; \
    jupyter nbextension enable --py --sys-prefix widgetsnbextension; \
    jupyter labextension install jupyter-leaflet; \
#    jupyter nbextension enable --py ipyleaflet; \
#    jupyter labextension install --no-build @bokeh/jupyter_bokeh@1.2.0; \
    jupyter labextension install --no-build @bokeh/jupyter_bokeh; \
#    jupyter labextension install --no-build @jupyter-widgets/jupyterlab-manager@1.1.0; \
    jupyter labextension install --no-build @jupyter-widgets/jupyterlab-manager; \
#    jupyter labextension install --no-build @jupyter-widgets/jupyterlab-sidecar@0.4.0; \
    jupyter labextension install --no-build @jupyter-widgets/jupyterlab-sidecar; \
#    jupyter labextension install --no-build bqplot@0.5.2; \
    jupyter labextension install --no-build bqplot@ ; \
#    jupyter labextension install --no-build jupyter-leaflet@0.11.7; \
    jupyter labextension install --no-build jupyter-matplotlib@0.5.0; \
    jupyter labextension install --no-build qgrid2@1.1.3; \
    jupyter labextension install --no-build @jupyter-voila/jupyterlab-preview ; \
    jupyter labextension install jupyterlab-topbar-extension jupyterlab-system-monitor ; \ 
    # Build javascript code
    jupyter lab build --dev-build=False; \
    # Clean up
    # See: https://github.com/jupyterlab/jupyterlab/issues/4930
    jupyter lab clean; \
    jlpm cache clean; \
    apt autoremove -yq; \
    echo 'Jupyterlab extensions enabling: OK'


ENV PATH /usr/local/texlive/2020/bin/x86_64-linux/:$PATH

## Add Tini
#ENV TINI_VERSION v0.18.0
#ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini

#RUN chmod +x /tini

USER $NB_UID

WORKDIR $HOME

EXPOSE 80
# Configure container startup

#ENTRYPOINT ["/tini", "-g", "--"]

CMD ["start-notebook.sh"]

# Copy local files as late as possible to avoid cache busting
COPY start.sh start-notebook.sh start-singleuser.sh /usr/local/bin/
#COPY jupyter_notebook_config.py /etc/jupyter/

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID

