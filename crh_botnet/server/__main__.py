from .server import *
import os,sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

initialize()
WSGIRequestHandler.protocol_version = "HTTP/1.1"  # for keep-alive
app.run(port=5003)
