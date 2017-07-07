import zmq

def tracing_server():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("ipc:///tmp/test1.pipe") # Using named pipes 

    while True:
        #  Wait for next request from client
        message = socket.recv()
        
        print("Received request server1: %s" % message)
        #reply = do_something(message) 

        #  Send reply back to client
        socket.send("")

if __name__ == "__main__":
    tracing_server()