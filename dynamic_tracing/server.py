import zmq
import json
import time
import os
import signal
import threading

clientPIDlist = set()
data = 0

def do_something(message): 
    if message:
        clientPID = int(message)
        global clientPIDlist
        if clientPID > 0:
            clientPIDlist.add(clientPID)
            reply = "added pid"
        if clientPID < 0:
            clientPIDlist.discard( - clientPID)
            reply = "removed pid"
    else:
        reply = "updated"
    return reply

def server():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("ipc:///tmp/test.pipe") # Using named pipes 

    while True:
        #  Wait for next request from client
        message = socket.recv()
        
        print("Received request: %s" % message)
        reply = do_something(message) + "Server data: %s" % data

        #  Send reply back to client
        socket.send(reply)

def controller_client():
    global data
    while True:
        time.sleep(10)
        data = data + 1
        for client in clientPIDlist:
            os.kill(client, signal.SIGIO)


if __name__ == "__main__":
    to_clients = threading.Thread(target=server)
    to_clients.start()
    controller_client()