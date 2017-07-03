import zmq
import json

def do_something(message): # Example: message='{"key": "val"}'
    #dictionary = json.loads(message)

    # Do something

    #reply = json.dumps(dictionary)
    reply = message
    return reply

def tracing_server():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("ipc:///tmp/test.pipe") # Using named pipes 

    while True:
        #  Wait for next request from client
        message = socket.recv()
        
        print("Received request: %s" % message)
        reply = do_something(message) 

        #  Send reply back to client
        socket.send(reply)

if __name__ == "__main__":
    tracing_server()
