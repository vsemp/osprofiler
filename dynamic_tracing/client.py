
import zmq
import json
import os
import signal
import atexit
import threading
import time

__local_ctx = threading.local()

def traceing_debug(function, comment=""): # need to change this to logging 
    str = function.__name__ + ": " + comment # but it's easier for me to debug with this at this point
    print(str + "\n")

def tracing_client(request=""):
    context = zmq.Context()

    #  Socket to talk to server
    traceing_debug(tracing_client, "Connecting to tracing server")
    socket = context.socket(zmq.REQ)
    socket.connect("ipc:///tmp/test.pipe") # Using named pipes 

    traceing_debug(tracing_client, "Sending request")
    socket.send(request)

    #  Get the reply.
    message = socket.recv()
    traceing_debug(tracing_client, "Received reply %s" % message)
    return message


def tracing_update():
    traceing_debug(tracing_update)
    assert(__local_ctx.tracing)
    __local_ctx.tracing = tracing_client()
    assert(__local_ctx.tracing)
    traceing_debug(tracing_update, __local_ctx.tracing)


def tracing_handler(signum, frame):
    tracing_update()


def tracing_release():
    tracing_client( str( - os.getpid()) )


def tracing_release_signals((signum, frame)):
    sys.exit(0)


def tracing_init():
    traceing_debug(tracing_init)
    if not hasattr(__local_ctx,"tracing"):
        signal.signal(signal.SIGIO, tracing_handler)
        signal.signal(signal.SIGTERM, tracing_release_signals)
        signal.signal(signal.SIGINT, tracing_release_signals)
        atexit.register(tracing_release)
        __local_ctx.tracing = tracing_client( str(os.getpid()) )
    assert(__local_ctx.tracing)
    traceing_debug(tracing_init, __local_ctx.tracing)


tracing_init()

for i in range(25):
    print(i)
    time.sleep(1)