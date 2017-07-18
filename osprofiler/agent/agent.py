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
    """
    Receives messages from 'connection_str' and puts them into 'queue'

    connection_str - type: string
    context        - type: class zmq.Context
    queue          - type: class gevent.queue.Queue
    """

    receiver_socket = context.socket(zmq.PULL)
    receiver_socket.bind(connection_str)
    print("Receiver started with the socket address: %s" % connection_str)

    while True:
        msg = receiver_socket.recv_json()
        print("Switched to the receiver thread for %s" % msg)
        queue.put(msg)


def mongo(connection_str, queue):
    """
    Wakes up when 'queue' is non-empty, grabs data from 'queue'
    and puts this data into MongoDB hosted at 'connection_str'

    connection_str - type: string
    queue          - type: class gevent.queue.Queue
    """

    try:
        from pymongo import MongoClient
    except ImportError:
        raise ImportError(
            "To use this command, you should install "
            "'pymongo' manually. Use command:\n "
            "'pip install pymongo'.")

    db_name = 'osprofiler'
    client = MongoClient(connection_str, connect=True)
    db = client[db_name]
    print("MongoDB thread started with the address: %s" % connection_str)

    while True:
        data = queue.get()
        print("Switched to MongoDB thread for %s" % data)
        db.profiler.insert_one(data)


def start_threads(ipc_connection_str, mongo_connection_str):
    """
    This function sets up how we run threads and starts them.

    ipc_connection_str   - type: string - socket address for IPC
    mongo_connection_str - type: string - address of MongoDB server
    """
    
    context = zmq.Context() # One global context for all green threads
    queue = Queue() # This is a queue that's used to synchronize green threads
    pool = Pool(2) # Use gevent.pool.ThreadPool to create regular (not green) threads
    pool.spawn(receiver, connection_str=ipc_connection_str, context=context, queue=queue)
    pool.spawn(mongo, connection_str=mongo_connection_str, queue=queue)
    pool.join() # Yield control and wait until green threads in 'pool' finish (wait forever) 


def main():
    # Need to rewrite this so that it reads some config file
    if len(sys.argv) == 1:
        ipc_connection_str = 'ipc:///tmp/tracing.pipe'
        mongo_connection_str = 'mongodb://localhost:27017'
    elif len(sys.argv) == 2:
        ipc_connection_str = sys.argv[2]
        mongo_connection_str = 'mongodb://localhost:27017'
    elif len(sys.argv) == 3:
        ipc_connection_str = sys.argv[2]
        mongo_connection_str = sys.argv[3]
    else:
        print("Incorrect number of arguments")
    start_threads(ipc_connection_str, mongo_connection_str)


if __name__ == '__main__':
    main()
