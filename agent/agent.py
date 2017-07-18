with open("/dev/shm/profiler_ipc", "wb") as f:                                           
    f.write(b"hi\n" + b"\0" * 4093) 