import ast
import sys
import os
import time
import subprocess
import argparse
import getpass
import re
import socket
import datetime
import json

from straight.plugin import load

from OpenSSL.crypto import load_pkcs12, FILETYPE_PEM, FILETYPE_ASN1, dump_certificate, dump_privatekey
from Crypto.PublicKey import RSA

from monroe.core import Scheduler, Experiment

# Paths for monroe certificates and keys

mnr_dir = os.path.expanduser('~/.monroe/')
mnr_key = str(mnr_dir) + 'mnrKey.pem'
mnr_crt = str(mnr_dir) + 'mnrCrt.pem'
sshkey = str(mnr_dir) + 'mnr_rsa.pub'
sshkey_priv = str(mnr_dir) + 'mnr_rsa'

import logging
logging.getLogger().setLevel(logging.DEBUG)

class MonroeCliPlugin:
    @classmethod
    def register_args(cls, subparsers):
        raise NotImplementedError("Cannot register an abstract plugin!")

def create(args):
    '''
    Function that creates an experiment based on the parameters given 
    to the argument parser
    '''
    scheduler = Scheduler(mnr_crt, mnr_key)
    exp = scheduler.new_experiment(
        args.name,
        args.script,
        args.nodecount,
        args.duration,
        testing=not(args.deployed))
    if args.ssh:
        if os.path.isfile(sshkey) and os.path.isfile(sshkey_priv):
            with open(sshkey, 'r') as f:
                key = f.read()
            exp.sshkey(key)
        else:
            inputv = input(
                "Default ssh key not found. Generate one now? [y/n]")
            if inputv in ['y', 'Y', 'yes', 'Yes']:
                gen_ssh_mnr()
            else:
                sys.exit(1)
    if args.traffic:
        exp.traffic(args.traffic * 1024 * 1024)
    if args.logfile:
        exp.shared(args.logfile * 1024 * 1024)
    if args.storage:
        exp.storage(args.storage * 1024 * 1024)
    if args.jsonstr:
        try:
            d_opt = make_dict(args.jsonstr)
        except Exception as err:
            print("Malformed options string: %s") % err
        exp.jsonstr(d_opt)

    if args.countries:
        c = []
        if 'Norway' in args.countries:
            c.append('no')
        if 'Sweden' in args.countries:
            c.append('se')
        if 'Italy' in args.countries:
            c.append('it')
        if 'Spain' in args.countries:
            c.append('es')
        exp.countries(c)
    if args.nodes:
       n = []
       n.append(args.nodes)
       exp.nodes(n)
    if args.recurrence:
        try:
            period = int(args.recurrence[0])
        except:
            raise SystemExit('Argument must be an integer')
        until = args.recurrence[1]
        if period < 3600:
            raise SystemExit(
                "The minimum period for recurring experiments must be at least 3600"
            )
        if (period % 3600) != 0:
            raise SystemExit("Recurrence period must be a multiple of 3600")
        try:
            date_t(until)
        except Exception as err:
            raise SystemExit(err)
    if args.maxnodes:
        maxnodes= scheduler.get_availability(exp).max_nodecount()
        print(maxnodes)
        exp.nodecount(maxnodes)
    if args.submit:
        a = scheduler.submit_experiment(exp)
        print(a.message())
        if 'Could not allocate' in a.message():
            sys.exit(1)
        expid = int(re.search(r'\d+', str(a)).group())
        if args.jsonstr:
            print("Additional options passed: " + str(d_opt))
        if args.ssh:
            print('Connecting to your experiment container:\n')
            item = scheduler.schedules(expid)[0]
            port = 30000 + item.nodeid()
            con = check_server('193.10.227.35', port)
            if con:
                cmd = " ".join([
                    'ssh', '-o', 'StrictHostKeyChecking=no', '-o',
                    'UserKnownHostsFile=/dev/null', '-i', sshkey_priv, '-p',
                    str(port), 'root@tunnel.monroe-system.eu'
                ])
                os.system(cmd)

    if args.availability:
        print(scheduler.get_availability(exp))

def make_dict(lst):
    '''Function which parses a list of strings into a dict'''
    d ={}
    for item in lst:
        pair = item.partition(":")
        if pair[2].startswith('[') and ']' in pair[2]:
            d[pair[0]] = pair[2].strip('[]').split(',')
        elif pair[2].startswith('{') and '}' in pair[2]:
           l =pair[2].strip('{}').split(', ')
           d[pair[0]]= make_dict(l)
        else:
            d[pair[0]] = pair[2]
    return d

def date_t(value):
    '''Function which checks a given string can be converted to a date within accepted scheduler ranges'''
    try:
        t = time.mktime(
            datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").timetuple())
    except:
        msg = "Incorrect date/time format!"
        raise argparse.ArgumentTypeError(msg)
    if t < time.time() or t > time.time() + 2678400:
        raise SystemExit("Date/time outside the acceptable ranges")
    return value


def gen_ssh_mnr():
    '''
    Function that generates and stores an RSA 2048 
    key for node login in OpenSSH format
    '''
    secret = getpass.getpass("Create export passphrase for the new key:")
    key = RSA.generate(2048)
    with open(sshkey, 'wb') as f:
        f.write(key.publickey().exportKey(format='OpenSSH'))
        print("Public key written to ~/.monroe/mnr_rsa.pub.")
    with open(sshkey_priv, 'wb') as f:
        if secret != "":
            f.write(key.exportKey(passphrase=secret))
        else:
            f.write(key.exportKey())
        print("Private key written to ~/.monroe/mnr_rsa.")
    os.chmod(sshkey_priv, 0o600)
    print("These are the default keys used by the cli.")


def check_server(address, port):
    '''
    Function that checks the reachability of a server
    on a specific port
    '''

    def spinning_cursor():
        while True:
            for cursor in '|/-\\':
                yield cursor

    print("Trying node " + str(port - 30000) + " on port " + str(port) + "...")
    spinner = spinning_cursor()
    s = socket.socket()
    dead = False
    start = time.time()
    while dead == False:
        try:
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            sys.stdout.write('\b')
            s.connect((address, port))
            print("Connection succeeded")
            return True
        except socket.error as e:
            time.sleep(1)
        if (time.time() - start) > 180:
            dead = True
            print("Could not contact the node.")
    return False


def handle_args(argv):
    '''
    Main argument handler, registers subparsers
    for the subcommands 'create', 'whoami', 'experiments',
    'quota', 'setup', 'delete' and 'results'
    '''
    parser = argparse.ArgumentParser(
        prog='monroe', description='Monroe Cli')
    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers(
        title="Experiment",
        description="The following commands can be used to create and submit experiments",
        metavar='Command',
        help='Description')
    parser_exp = subparsers.add_parser('create', help='Creates an experiment')
    parser_exp.set_defaults(func=create)

    parser_exp.add_argument(
        '--name', type=str, help='Sets the experiment name')
    parser_exp.add_argument(
        '--deployed',
        action='store_true',
        help='Sets the nodetype to Deployed, default is Testing')
    parser_exp.add_argument(
        '--script',
        default='monroe/base',
        help='Sets the Docker image to deploy, default is monroe/base')
    parser_exp.add_argument(
        '--nodecount',
        type=int,
        default=1,
        help='Sets the number of nodes to deploy on, default is 1')
    parser_exp.add_argument(
        '--maxnodes',
        action='store_true',
        help='Sets the experiment for the maximum number of nodes')
    parser_exp.add_argument(
        '--duration',
        type=int,
        default=300,
        help='Sets the experiment duration, default is 300')
    parser_exp.add_argument(
        '--start',
        type=date_t,
        default=0,
        help='Sets a start time in the future, format Y-m-dTH:M:S')
    parser_exp.add_argument(
        '--traffic',
        type=int,
        default=1,
        help='Sets the active data quota in MB, default is 1')
    parser_exp.add_argument(
        '--storage',
        type=int,
        default=128,
        help='Sets the deployment storage quota in MB, default is 128')
    parser_exp.add_argument(
        '--logfile',
        type=int,
        default=0,
        help='Sets the log file quota in MB, default is 0')
    parser_exp.add_argument(
        '--ssh',
        action='store_true',
        help='Path to your ssh key for remoting into nodes')
    parser_exp.add_argument(
        '--jsonstr',
        nargs='+',
        help='Additional options string, formatted as key:value pairs. Example: <apple:sour orange:tasty banana:"[yellow,yummy]" vegetables:"{broccoli:green, tomato:[red,juicy]}">' 
    )
    parser_exp.add_argument(
        '--countries',
        nargs='?',
        help='Countries: pick one or several from Norway, Sweden, Spain, Italy')
    parser_exp.add_argument(
        '--nodes',
        nargs='+',
        type=int,
        help='Specific node IDs')
    parser_exp.add_argument(
        '--recurrence',
        nargs=2,
        metavar='<period, finish time>',
        help='Defines recurrence parameters')
    parser_exp.add_argument(
        '--submit', action='store_true', help='Submit the experiment')
    #parser_exp.add_argument('--save', action='store_true', help = 'Sets the experiment name')
    parser_exp.add_argument(
        '--availability',
        action='store_true',
        help='Check experiment availability')

    parser_whoami = subparsers.add_parser(
        'whoami', help='Displays MONROE user details')
    parser_whoami.set_defaults(func=whoami)

    parser_quota = subparsers.add_parser(
        'quota', help='Displays MONROE quota details')
    parser_quota.set_defaults(func=quota)

    parser_experiments = subparsers.add_parser(
        'experiments', help='Display recent experiments')
    parser_experiments.add_argument(
        '--max',
        metavar='<number>',
        type=int,
        default=10,
        help='Maximum number of experiments to display')
    parser_experiments.set_defaults(func=experiments)

    parser_setup = subparsers.add_parser(
        'setup',
        help='Specifies MONROE user certificate to use for accessing the scheduler'
    )
    parser_setup.set_defaults(func=setup)
    parser_setup.add_argument(
        '--cert',
        metavar='<filename>',
        help='Location of the certificate file')

    parser_delete = subparsers.add_parser(
        'delete', help='Deletes an experiment')
    parser_delete.set_defaults(func=delete)
    parser_delete.add_argument(
        '--exp',
        metavar='<exp-id>',
        type=int,
        help='ID of the experiment you want to delete')

    parser_results = subparsers.add_parser(
        'results', help='Downloads the results for an experiment')
    parser_results.set_defaults(func=results)
    parser_results.add_argument(
        '--exp',
        metavar='<exp-id>',
        type=int,
        help='ID of the experiment you want to download')

    plugins = load("monroe.plugins", subclasses=MonroeCliPlugin)
    for plugin in plugins:
        plugin.register_args(subparsers)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(argv[1:])
    # Validation of cert and key required before executing commands on the scheduler
    if args.func != setup:
        if not os.path.isfile(mnr_key) or not os.path.isfile(mnr_crt):
            raise SystemExit(
                "Please run monroe setup --cert <certificate> to be able to submit experiments and retrieve results."
            )
        try:
            scheduler = Scheduler(mnr_crt, mnr_key)
            auth = scheduler.auth()
        except:
            raise SystemExit(
                "Something went wrong.\nTry running monroe setup --cert <certificate>\nto refresh your certificate and check the scheduler is running\nand can be accessed from your local network."
            )
        args.func(args)
    else:
        args.func(args)


def setup(args):
    '''
    Function that sets up the files necessary to the
    interaction with the scheduler
    '''
    if args.cert:
        if os.path.isfile(args.cert):
            try:
                with open(args.cert, 'rb') as f:
                    cert = f.read()
                passphrase = getpass.getpass("Enter passphrase:")
                c = load_pkcs12(cert, passphrase)
                certificate = c.get_certificate()
                private_key = c.get_privatekey()
                type_ = FILETYPE_PEM
                pk = dump_privatekey(type_, private_key)
                ct = dump_certificate(type_, certificate)
                if not os.path.exists(mnr_dir):
                    os.makedirs(mnr_dir)
                with open(mnr_key, 'wb') as f:
                    f.write(pk)
                with open(mnr_crt, 'wb') as f:
                    f.write(ct)
            except Exception as err:
                raise SystemExit('ERROR: %s' % str(err))
            print("Your certificate files were stored in ~/.monroe")
        else:
            raise SystemExit("File not found!")
    else:
        print("Please specify a p12 or pkcs12 certificate to use.")


def delete(args):
    '''
    Function that deletes experiments based on the 
    experiment id passed to the parser
    '''
    if args.exp:
        scheduler = Scheduler(mnr_crt, mnr_key)
        try:
            a = scheduler.delete_experiment(args.exp)
            print(a['message'])
        except Exception as err:
            raise SystemExit("ERROR: %s" % str(err))
    else:
        print("Please specify the ID of the experiment you want to delete.")


def results(args):
    '''
    Function that downloads experiment results based on the 
    experiment id passed to the parser
    '''
    if args.exp:
        scheduler = Scheduler(mnr_crt, mnr_key)
        scheduler.result(args.exp)
    else:
        print("Please specify an experiment ID to get results for.")


def whoami(args):
    '''
    Function that prints user identity
    '''
    scheduler = Scheduler(mnr_crt, mnr_key)
    print(scheduler.auth())


def quota(args):
    '''
    Function that prints user quota
    '''
    scheduler = Scheduler(mnr_crt, mnr_key)
    for i in scheduler.journals()[-3:]:
        print(i)


def experiments(args):
    '''
    Function that prints with user experiments
    '''
    scheduler = Scheduler(mnr_crt, mnr_key)
    for i in scheduler.experiments()[-args.max:]:
        print(i)

def main():
    handle_args(sys.argv)

if __name__ == "__main__":
    main()
