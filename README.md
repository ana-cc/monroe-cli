Installing in a Debian 9 VM

```apt install git, python3-setuptools, build-essentials libffi-dev libssl-dev python3-straight.plugin python3-cryptography 
git clone https://github.com/ana-cc/monroe-cli.git
cd monroe-cli
python3 setup.py develop```
The above should install the latest version of the cli. Copy the certificate across to your Debian VM and setup your environment:
```monroe setup <certificate>```
