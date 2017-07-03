import zmq
import json

def tracing_client(request="Hello"):
    context = zmq.Context()

    #  Socket to talk to server
    print("Connecting to tracing server")
    socket = context.socket(zmq.REQ)
    socket.connect("ipc:///tmp/test.pipe") # Using named pipes 

    print("Sending request")
    socket.send(request)

    #  Get the reply.
    message = socket.recv()
    print("Received reply %s" % message)
    return message

if __name__ == "__main__":
    if tracing_client():
        print("True")
