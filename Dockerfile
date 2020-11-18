FROM ubuntu:18.04 as builder

USER root

ARG AZURE_STORAGE_CONNECTION_STRING
ARG GENESIS_PATH=/opt/culedger-core/sovrin/pool_transactions_live_genesis
ARG INSTITUTION_NAME=TestHarness
ARG INSTITUTION_LOGO=http://example.com/logo.png

# install dependencies
RUN apt-get -y update && apt-get install -y --no-install-recommends \
    software-properties-common \
    curl \
    gnupg2 \
    ca-certificates \
    apt-transport-https \
    lsb-release

RUN curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.asc.gpg

#ENV AZ_REPO=$(lsb_release -cs) currently bionic
RUN echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ bionic main" > /etc/apt/sources.list.d/azure-cli.list

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88 && \
    add-apt-repository "deb https://repo.sovrin.org/sdk/deb bionic stable"

RUN apt-get -y update && apt-get -y install \
  indy-cli \
  libindy \
  libnullpay \
  libvcx \
  curl \
  python3 \
  python3-pip \
  python3-setuptools \
  libssl1.0.0 \
  libzmq3-dev \
  vim \
  zip \
  jq \
  azure-cli

RUN pip3 install wheel &&\
    pip3 install python3-indy &&\
    pip3 install python3-wrapper-vcx &&\
    pip3 install azure-storage-queue &&\
    pip3 install opencensus-ext-azure

ADD . /opt/culedger-core/

ENV AZURE_STORAGE_CONNECTION_STRING ${AZURE_STORAGE_CONNECTION_STRING}
ENV GENESIS_PATH ${GENESIS_PATH}
ENV INSTITUTION_NAME ${INSTITUTION_NAME}
ENV INSTITUTION_LOGO ${INSTITUTION_LOGO}

ENTRYPOINT ["/opt/culedger-core/scripts/entrypoint.sh"]
CMD ["cd .. && ./start_emulator_monitors.sh"]
