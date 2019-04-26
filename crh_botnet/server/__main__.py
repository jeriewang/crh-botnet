from .server import *
import os,sys

os.chdir('/var/tmp/')

initialize()
WSGIRequestHandler.protocol_version = "HTTP/1.1"  # for keep-alive
app.run('0.0.0.0',port=5003)
