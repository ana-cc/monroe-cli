import sys
import os
import subprocess
import argparse
import getpass
import re
from monroe.core import Scheduler, Experiment
from OpenSSL.crypto import load_pkcs12, FILETYPE_PEM, FILETYPE_ASN1, dump_certificate, dump_privatekey


mnr_dir = os.path.expanduser('~/.monroe/')
mnr_key = str(mnr_dir)+'mnrKey.pem'
mnr_crt = str(mnr_dir)+'mnrCrt.pem'


def create(args):
    
    scheduler = Scheduler(mnr_crt, mnr_key)
    exp = scheduler.new_experiment(args.name, args.script, args.nodecount, args.duration, testing=args.testing)
    if args.sshkey:
        exp.sshkey(args.sshkey)
    if args.availability:
        print (scheduler.get_availability(exp))
    if args.submit:
        a = scheduler.submit_experiment(exp)
        expid = int(re.search(r'\d+', str(a)).group())
        print(a.message())
    if args.sshkey:
        print ('To connect to your experiment container(s):\n')
        for item in scheduler.schedules(expid):
           print("ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i your_private_key -p " + str(30000 + item.nodeid()) + " root@tunnel.monroe-system.eu")

        
 

def handle_args(argv):
    parser = argparse.ArgumentParser(prog='monroe-cli', description='Monroe Cli')
    parser.set_defaults(func=None)

    parser.add_argument('--setup', metavar='<certificate>', type=str, help = 'Specifies MONROE user certificate to use for accessing the scheduler')
    parser.add_argument('--auth', action='store_true', help = 'Displays MONROE user details')
    parser.add_argument('--quota', action='store_true', help = 'Displays MONROE quota details')
    parser.add_argument('--experiments', metavar='<number>', type=int, nargs='?', const=10, help = 'Displays MONROE user details')
    parser.add_argument('--delete', metavar='<experiment-id>', help = 'Deletes an experiment')
    parser.add_argument('--result', metavar='<experiment-id>', help = 'Downloads the results for an experiment')
    #parser.add_argument('--submit', metavar='<input-file>', help='Submits an experiment from a json file')

    subparsers = parser.add_subparsers(title="Experiment", description="The following commands can be used to create and submit experiments", metavar='COMMAND', help='Description')    
    parser_exp = subparsers.add_parser('create', help='Creates an experiment')
    parser_exp.set_defaults(func=create)

    parser_exp.add_argument('--name', type=str, help = 'Sets the experiment name')
    parser_exp.add_argument('--testing', action='store_true', help = 'Sets the nodetype to Testing, default is Deployed')
    parser_exp.add_argument('--script', type=str, default='monroe/base', help = 'Sets the Docker image to deploy, default is monroe/base')
    parser_exp.add_argument('--nodecount', type=int, default = 1, help = 'Sets the number of nodes to deploy on, default is 1')
    parser_exp.add_argument('--duration', type=int, default = 300, help = 'Sets the experiment duration, default is 300')
    parser_exp.add_argument('--sshkey', type=str, help = 'Path to your ssh key for remoting into nodes')
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

