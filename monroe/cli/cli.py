import sys
import os
import time
import subprocess
import argparse
import getpass
import re
from monroe.core import Scheduler, Experiment
from OpenSSL.crypto import load_pkcs12, FILETYPE_PEM, FILETYPE_ASN1, dump_certificate, dump_privatekey
import datetime
import json

mnr_dir = os.path.expanduser('~/.monroe/')
mnr_key = str(mnr_dir)+'mnrKey.pem'
mnr_crt = str(mnr_dir)+'mnrCrt.pem'


def create(args):
    
    scheduler = Scheduler(mnr_crt, mnr_key)
    exp = scheduler.new_experiment(args.name, args.script, args.nodecount, args.duration, testing=args.testing)
    if args.sshkey:
        if os.path.isfile(args.sshkey):
           with open(args.sshkey, 'r') as f:
               key = f.read()
           exp.sshkey(key)
        else:
           print ("File does not exist!") 
    if args.traffic:
        exp.traffic(args.traffic)
    if args.logfile:
        exp.shared(args.logfile)
    if args.storage:
        exp.storage(args.storage)
    if args.availability:
        print (scheduler.get_availability(exp))
    if args.jsonstr:
        exp.jsonstr(args.jsonstr)
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

    if args.submit:
        a = scheduler.submit_experiment(exp)
        print(a.message())
        if 'Could not allocate' in a.message():
            sys.exit(1)
        expid = int(re.search(r'\d+', str(a)).group())
        if args.sshkey:
            print ('To connect to your experiment container(s):\n')
            for item in scheduler.schedules(expid):
                print("ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i your_private_key -p " + str(30000 + item.nodeid()) + " root@tunnel.monroe-system.eu")

        
def date_t(value):
    try:
        t = time.mktime(datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").timetuple())
    except:
        msg = "Incorrect date/time format!"
        raise argparse.ArgumentTypeError(msg)
    if t < time.time() or t > time.time() + 2678400:
        print("Date/time outside the acceptable ranges")
        sys.exit(1)
    return value

def handle_args(argv):
    parser = argparse.ArgumentParser(prog='monroe-cli', description='Monroe Cli')
    parser.set_defaults(func=None)

    parser.add_argument('--setup', metavar='<certificate>', type=str, help = 'Specifies MONROE user certificate to use for accessing the scheduler')
    parser.add_argument('--auth', action='store_true', help = 'Displays MONROE user details')
    parser.add_argument('--quota', action='store_true', help = 'Displays MONROE quota details')
    parser.add_argument('--experiments', metavar='<number>', type=int, nargs='?', const=10, help = 'Displays MONROE user details')
    parser.add_argument('--delete', metavar='<experiment-id>', help = 'Deletes an experiment')
    parser.add_argument('--result', metavar='<experiment-id>', help = 'Downloads the results for an experiment')
    parser.add_argument('--submit', metavar='<input-file>', help='Submits an experiment from a json file')

    subparsers = parser.add_subparsers(title="Experiment", description="The following commands can be used to create and submit experiments", metavar='COMMAND', help='Description')    
    parser_exp = subparsers.add_parser('create', help='Creates an experiment')
    parser_exp.set_defaults(func=create)

    parser_exp.add_argument('--name', type=str, help = 'Sets the experiment name')
    parser_exp.add_argument('--testing', action='store_true', help = 'Sets the nodetype to Testing, default is Deployed')
    parser_exp.add_argument('--script', default='monroe/base', help = 'Sets the Docker image to deploy, default is monroe/base')
    parser_exp.add_argument('--nodecount', type=int, default = 1, help = 'Sets the number of nodes to deploy on, default is 1')
    parser_exp.add_argument('--duration', type=int, default = 300, help = 'Sets the experiment duration, default is 300')
    parser_exp.add_argument('--start', type=date_t, default = 0, help = 'Sets a start time in the future, format Y-m-dTH:M:S')
    parser_exp.add_argument('--traffic', type=int, default = 1, help = 'Sets the active data quota in MB, default is 1')
    parser_exp.add_argument('--storage', type=int, default = 128, help = 'Sets the deployment storage quota in MB, default is 128')
    parser_exp.add_argument('--logfile', type=int, default = 0, help = 'Sets the log file quota in MB, default is 0')
    parser_exp.add_argument('--sshkey', help = 'Path to your ssh key for remoting into nodes')
    parser_exp.add_argument('--jsonstr', nargs='?', help = 'Additional options string. It will automatically be converted to JSON.')
    parser_exp.add_argument('--countries', nargs='?', help = 'Countries: pick one or several from Norway, Sweden, Spain, Italy')
    parser_exp.add_argument('--submit', action='store_true', help = 'Submit the experiment')
    #parser_exp.add_argument('--save', action='store_true', help = 'Sets the experiment name')
    parser_exp.add_argument('--availability', action='store_true', help = 'Check experiment availability')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(argv[1:])
    if args.func:
        args.func(args)

    if args.setup:
        if os.path.isfile(args.setup):
            try:
               with open(args.setup, 'rb') as f:
                  cert = f.read()
               passphrase = getpass.getpass()   
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
                print('ERROR: %s' % str(err))
                sys.exit(1)
            print("Your certificate files were stored in ~/.monroe")
        else: 
            print("File not found!")
            sys.exit(1)
        
    if not os.path.isfile(mnr_key) or not os.path.isfile(mnr_crt):
        print ("Please run monroe-cli --setup <certificate> to be able to submit experiments and retrieve results.")
        sys.exit(1)
    try:
        scheduler = Scheduler(mnr_crt, mnr_key)
        auth = scheduler.auth()
    except:
        print ("Something went wrong.\nTry running monroe-cli --setup <certificate>\nto refresh your certificate and check the scheduler is running\nand can be accessed from your local network.")
        sys.exit(1)

    if args.auth:
       print (scheduler.auth())
      
    if args.experiments:
       for i in scheduler.experiments()[-args.experiments:]:
           print(i)
 
    if args.quota:
       for i in scheduler.journals()[-3:]:
           print(i)
 
    if args.delete:
       try:
           a = scheduler.delete_experiment(args.delete)
           print (a['message'])
       except Exception as err:
           print("ERROR: %s" % str(err))
           sys.exit(1)

    if args.result:
       scheduler.result(args.result)
      

 
if __name__ == "__main__":
    handle_args(sys.argv)

