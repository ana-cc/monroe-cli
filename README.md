## Installing in a Debian 9 VM

The following will install the latest version of the cli:

```
apt install git python3-setuptools build-essentials libffi-dev libssl-dev python3-straight.plugin python3-cryptography
git clone https://github.com/ana-cc/monroe-cli.git
cd monroe-cli
python3 setup.py develop
```
To set up your certificate, copy your pkcs12 certificate to the new VM, and run:

```monroe setup <certificate-file>```

## Notes:

The tool generates an ssh key to use for ssh-ing into the nodes, it asks the user to proceed with the key generation it can't find one in ~/.monroe

The tool depends on having crt and key files for an experimenter certificate in ~/.monroe/. This is automated by running ```monroe setup <cert.p12>``` on a fed4fire pkcs12 certificate, which creates a .monroe folder in your home directory, and extracts the cert and key in pem format.

## Library:

The library can be imported as such:
```from monroe.core import *```

The public funtions are all documented and it should be straightforward
to use. The following example creates a scheduler, adds an experiment, modifies it and submits it:

```from monroe.core import *
s = Scheduler("/home/user/.monroe/mnrCrt.pem", "/home/user/.monroe/mnrKey.pem")
e = s.new_experiment()
e.script('user/dockercontainer')
e.name('myexperiment')
e.countries('Norway,VTAB)
e.nodecount('20')
s.submit_experiment(e)
```

The following example creates a scheduler, and retrieves list of nodes in a particular country:

```from monroe.core import *
s = Scheduler("/home/user/.monroe/mnrCrt.pem", "/home/user/.monroe/mnrKey.pem")
nodelist = [node.id() for node in s.nodes() if node.site() == 'spain']
```
