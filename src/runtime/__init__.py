try:
    from .environment import (
        Result, Ok, Err, FileSystemAPI, OperatingSystemAPI, HttpAPI,
        Channel, channel, spawn, addr, peek, memdump, delay_ms, get_runtime_env
    )
except (ImportError, ValueError):
    from environment import (
        Result, Ok, Err, FileSystemAPI, OperatingSystemAPI, HttpAPI,
        Channel, channel, spawn, addr, peek, memdump, delay_ms, get_runtime_env
    )
