FROM monroe/base

MAINTAINER jonas.karlsson@kau.se

#APT OPTS
ENV APT_OPTS -y --allow-downgrades --allow-remove-essential --allow-change-held-packages --no-install-recommends --no-install-suggests --allow-unauthenticated

# Add a volume to store certificates
VOLUME /root/.monroe

# We do not add a volume for the results as one
# most likely wants to bind mounted to some host directory
#VOLUME /results

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get install ${APT_OPTS} \
    git \
    python3-dev \
    python3-setuptools \
    build-essential \
    libffi-dev \
    libssl-dev \
    python3-straight.plugin \
    python3-cryptography \
    # Fix missing packages
    && apt-get update ${APT_OPTS} --fix-missing \
    #Configure and build monroe-cli
    && git clone https://github.com/MONROE-PROJECT/monroe-cli.git && cd monroe-cli \
    && python3 setup.py develop && cd / \
    # Cleanup
    && apt-get purge  ${APT_OPTS} \
    python3-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    git \
    && apt-get clean ${APT_OPTS} \
    && apt-get autoremove ${APT_OPTS} \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/doc /usr/share/man /usr/share/locale /var/cache/debconf/*-old dumb-init.deb

WORKDIR /results/

ENTRYPOINT ["dumb-init", "--", "/usr/local/bin/monroe"]
