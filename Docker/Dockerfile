FROM debian:stretch

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y ssh wget git python3-dev python3-setuptools build-essential libffi-dev libssl- dev python3-straight.plugin python3-cryptography ca-certificates && apt-get clean 

RUN mkdir /root/.monroe/
RUN mkdir /root/results/
RUN git clone https://github.com/ana-cc/monroe-cli
COPY files/* /root/.monroe/

RUN ssh-keygen -t rsa -P "" -f /root/.monroe/mnr_rsa

RUN openssl pkcs12 -in /root/.monroe/cert.p12 -out /root/.monroe/mnrCrt.pem -clcerts -nokeys -passin pass:yourpassword
RUN openssl pkcs12 -in /root/.monroe/cert.p12 -out /root/.monroe/mnrKey.pem -nocerts -nodes -passin pass:yourpassword

WORKDIR monroe-cli
RUN python3 setup.py develop
WORKDIR /root/results
ENTRYPOINT ["/usr/local/bin/monroe"]
~
