"""
Created on Fri Jul 14 07:02:39 2017

@author: vladimir
"""


from osprofiler.drivers import base
from osprofiler import exc

import threading


class IPC(base.Driver):
    def __init__(self, connection_str, project=None,
                 service=None, host=None, **kwargs):
        """IPC driver based on ZeroMQ for OSProfiler."""

        super(IPC, self).__init__(connection_str, project=project,
                                      service=service, host=host)
        
        try:
            import zmq.green
        except ImportError:
            raise exc.CommandError(
                "To use this command, you should install "
                "'ZeroMQ' manually. Use command:\n "
                "'pip install zmq'.")
        
        self.context = zmq.green.Context() # The same context is used across many threads

    @classmethod
    def get_name(cls):
        return 'ipc' # This name should coinside with the beginning of connection_str

    def notify(self, info):
        """Send notifications to another process on this node.

        :param info:  Contains information about trace element.
                      In payload dict there are always 3 ids:
                      "base_id" - uuid that is common for all notifications
                                  related to one trace. Used to simplify
                                  retrieving of all trace elements from
                                  the database.
                      "parent_id" - uuid of parent element in trace
                      "trace_id" - uuid of current element in trace

                      With parent_id and trace_id it's quite simple to build
                      tree of trace elements, which simplify analyze of trace.

        """
        thread_local_storage = threading.local()
        # ZeroMQ sockets are not thread safe. That's why we need to create a socket per thread
        if not getattr(thread_local_storage, 'profiler_ipc', None):
            try:
                import zmq.green # This is for green threads. Google zmq.green vs zmq for details
            except ImportError:
                raise exc.CommandError(
                    "To use this command, you should install "
                    "'ZeroMQ' manually. Use command:\n "
                    "'pip install zmq'.")
            thread_local_storage.profiler_ipc = {'socket': self.context.socket(zmq.green.PUSH)}
            thread_local_storage.profiler_ipc['socket'].connect(self.connection_str)
        
        data = info.copy()
        data['project'] = self.project
        data['service'] = self.service
        
        thread_local_storage.profiler_ipc['socket'].send_json(data)
