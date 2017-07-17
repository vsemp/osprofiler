"""
Created on Fri Jul 14 07:02:39 2017

@author: vladimir
"""

import sys
import gevent
import zmq.green as zmq

from gevent.queue import Queue
from gevent.pool import Pool

def receiver(connection_str, context, queue):
    receiver_socket = context.socket(zmq.PULL)
    receiver_socket.bind(connection_str)
    print("Receiver started with the socket address: %s" % connection_str)

    while True:
        msg = receiver_socket.recv_json()
        print("Switched to the receiver thread for %s" % msg)
        queue.put(msg)

def mongo(connection_str, context, queue):
    use_real_mongodb = True
    try:
        from pymongo import MongoClient
    except ImportError:
        print(
            "\n\n\nTo use this command, you should install "
            "'pymongo' manually. Use command:\n "
            "'pip install pymongo'.\n\n\n")
        use_real_mongodb = False

    if use_real_mongodb:
        db_name = 'osprofiler'
        client = MongoClient(connection_str, connect=True)
        db = client[db_name]
        print("MongoDB thread started with the address: %s" % connection_str)

    while True:
        data = queue.get()
        print("Switched to MongoDB thread for %s" % data)
        if use_real_mongodb:
            db.profiler.insert_one(data)


def sender(connection_str, context):
    while True:
        sender_socket = context.socket(zmq.PUSH)
        sender_socket.connect(connection_str)
        print("Receiver started with the socket address: %s" % connection_str)
        sender_socket.send_json({'here should be': "trace"})
        gevent.sleep(1)

def start_threads(ipc_connection_str, mongo_connection_str):
    context = zmq.Context()
    queue = Queue()
    pool = Pool(3)
    pool.spawn(receiver, connection_str=ipc_connection_str, context=context, queue=queue)
    pool.spawn(mongo, connection_str=mongo_connection_str, context=context, queue=queue)
    pool.spawn(sender, connection_str=ipc_connection_str, context=context)
    pool.join()

def main():
    if len(sys.argv) == 1:
        ipc_connection_str = "ipc:///tmp/tracing.pipe"
        mongo_connection_str = 'mongodb://localhost:27017'
    else:
        print("Arguments are not implemented yet")
    start_threads(ipc_connection_str, mongo_connection_str)
        
if __name__ == "__main__":
    main()