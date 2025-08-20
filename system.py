from __future__ import annotations

import socket
from fastapi import APIRouter


router = APIRouter()


@router.get("/lan-info", response_model=dict)
def lan_info():
    hostname = socket.gethostname()
    ip = "127.0.0.1"
    try:
        ip = socket.gethostbyname(hostname)
    except:
        pass
    return {"hostname": hostname, "ip": ip}


