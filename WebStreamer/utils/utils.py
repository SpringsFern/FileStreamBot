from aiohttp import web
from collections import defaultdict
from typing import Dict

from WebStreamer.vars import Var

ongoing_requests: Dict[str, int] = defaultdict(lambda: 0)

def get_requester_ip(req: web.Request) -> str:
    if Var.TRUST_HEADERS:
        try:
            return req.headers["X-Forwarded-For"]
        except KeyError:
            pass
    peername = req.transport.get_extra_info('peername')
    if peername is not None:
        return peername[0]

def allow_request(ip: str) -> None:
    return ongoing_requests[ip] < Var.REQUEST_LIMIT

def increment_counter(ip: str) -> None:
    ongoing_requests[ip] += 1

def decrement_counter(ip: str) -> None:
    ongoing_requests[ip] -= 1