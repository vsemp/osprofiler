Usage of IPC driver with an agent
=================================
To set up and use IPC driver and the agents model for collection of traces follow these steps:

* Install ZeroMQ with ``pip install zmq``
* Install gevent library with ``pip install gevent``
* Install `MongoDB <https://docs.mongodb.com/getting-started/shell/tutorial/install-mongodb-on-red-hat/>`_  and run it on ``localhost:27017`` 
* Find your OSprofiler directory <osprofiler> and open it::

    import osprofiler
    print(osprofiler.__file__)

* *Optional:* make sure you can run ``python <osprofiler>/agent/playwithme.py`` then kill this process
* Start the agent process in the background ``python <osprofiler>/agent/agent.py &``
* Edit Cinder config file, on my VM it's ``/etc/cinder/cinder.conf``, so that it has something like::

    [profiler]
    enabled = True
    connection_string = ipc:///tmp/tracing.pipe
    hmac_keys = SECRET_KEY

  Triple slash here is not a mistake. To use IPC driver ``connection_string`` needs to be ``ipc://<path to file>``. Use the HMAC key you specified for OSprofiler instead of ``SECRET_KEY``
* *Optional:* make sure you can collector traces with ``connection_string = mongodb://localhost:27017`` instead.
* Restart Cinder. On my VM the following commands work::

    sudo systemctl restart devstack@c-api.service
    sudo systemctl restart devstack@c-sch.service
    sudo systemctl restart devstack@c-vol.service
    sudo systemctl | grep devstack@c-

* Try ``cinder --profile SECRET_KEY list``. The agent ``agent.py`` prints all tracepoints it receives. You can comment out these print statements in ``agent.py``
* Then run::

    osprofiler trace show --connection-string mongodb://localhost:27017 --json <base ID>

  Put the desired trace base ID into the field <base ID>
