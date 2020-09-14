# vi: ft=Dockerfile
#
# https://jtreminio.com/blog/running-docker-containers-as-current-host-user/#ok-so-what-actually-works
# https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
#
#-----------------------------------------------------------------------------------------

FROM registry.gitlab.com/klimavro/base-image/bionic:py37-20200411

# Create a normal user
ARG USER_NAME=amigo
ARG USER_ID=1000
ARG GROUP_ID=1000

ENV USER_NAME=${USER_NAME}
ENV USER_ID=${USER_ID}
ENV GROUP_ID=${GROUP_ID}
ENV USER_HOME=/home/${USER_NAME}

RUN set -xeu; \
    # Add the user
    groupadd -g ${GROUP_ID} ${USER_NAME}; \
    useradd -u ${USER_ID} -g ${GROUP_ID} -m -s /bin/bash ${USER_NAME}; \
    usermod -a -G users ${USER_NAME}; \
    echo "Creating user ${USER_NAME}: OK";

# Switch to the normal user
USER ${USER_NAME}

# setup virtualenv
ENV VIRTUAL_ENV=${USER_HOME}/.venv
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

RUN set -xe; \
    echo 'Create virtualenv'; \
    python3.7 -m venv ${VIRTUAL_ENV}; \
    pip install -U pip; \
    find ${VIRTUAL_ENV} -name *.pyc -delete; \
    echo 'done'

ARG DEPLOY_ENV=prod
ENV DEPLOY_ENV=${DEPLOY_ENV}

# Install some basic requirements to take advantage of layer-caching
COPY ./requirements/requirements-dev.txt \
     ./requirements/requirements.txt \
     # destination
     /tmp/

# Install any new requirements
RUN set -xe; \
    echo 'Install dependencies'; \
    pip install --no-cache -r /tmp/requirements-dev.txt; \
    find ${VIRTUAL_ENV} -name *.pyc -delete; \
    echo 'done'

# Copy executable scripts to the root
COPY ./docker/entrypoint_inject.sh \
     ./docker/start.sh \
     ./docker/start_reload.sh \
     ./docker/prestart.sh \
     ./docker/wait_for_port.py \
     # destination
     /usr/local/bin/

#USER root
#RUN set -xeu; \
    #apt update; \
    #apt install -yq gnupg; \
    #curl http://nginx.org/keys/nginx_signing.key | apt-key add - ;\
    #touch '/etc/apt/sources.list.d/nginx.list'; \
    #echo 'deb [arch=amd64] http://nginx.org/packages/mainline/ubuntu/ bionic nginx' >> '/etc/apt/sources.list.d/nginx.list'; \
    #echo 'deb-src http://nginx.org/packages/mainline/ubuntu/ bionic nginx' >> '/etc/apt/sources.list.d/nginx.list'; \
    #apt update; \
    #apt install -yq nginx; \
    #echo 'nginx installation OK';

ENTRYPOINT ["/usr/local/bin/entrypoint_inject.sh"]
CMD ["/usr/local/bin/start.sh"]

ENV APPDIR=${USER_HOME}/app
COPY ./ ${APPDIR}
WORKDIR ${APPDIR}

# we will switch back to the normal user via the entrypoint
USER root
