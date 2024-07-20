# Taken from megadlbot_oss <https://github.com/eyaadh/megadlbot_oss/blob/master/mega/webserver/routes.py>
# Thanks to Eyaadh <https://github.com/eyaadh>

import time
import logging
import mimetypes
import traceback
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from WebStreamer.bot import multi_clients, work_loads, StreamBot
from WebStreamer.utils.utils import allow_request, get_requester_ip, get_readable_time, ongoing_requests
from WebStreamer.vars import Var
from WebStreamer.server.exceptions import FIleNotFound
from WebStreamer import StartTime, __version__
from WebStreamer.utils.paralleltransfer import ParallelTransferrer


routes = web.RouteTableDef()
class_cache = {}

@routes.get("/status", allow_head=True)
async def root_route_handler(request: web.Request):
    return web.json_response(
        {
            "server_status": "running",
            "uptime": get_readable_time(time.time() - StartTime),
            "telegram_bot": "@" + StreamBot.username,
            "connected_bots": len(multi_clients),
            "loads": dict(
                ("bot" + str(c + 1), l)
                for c, (_, l) in enumerate(
                    sorted(work_loads.items(), key=lambda x: x[1], reverse=True)
                )
            ),
            "ongoing_requests": ongoing_requests if request.query.get("id") == Var.API_HASH else  None ,
            "version": __version__,
        }
    )

@routes.head("/dl/{path}")
@routes.head("/dl/{path}/{name}")
async def stream_handler(request: web.Request):
    return await media_streamer(request, True)

@routes.get("/dl/{path}", allow_head=False)
@routes.get("/dl/{path}/{name}", allow_head=False)
async def stream_handler(request: web.Request):
    try:
        return await media_streamer(request, False)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.error(traceback.format_exc())
        raise web.HTTPInternalServerError(text=str(e))

async def media_streamer(request: web.Request, head: bool=False):
    msg_id = int(request.match_info["path"])
    ip = get_requester_ip(request)
    range_header = request.headers.get("Range", 0)
    
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]
    
    if Var.MULTI_CLIENT:
        logging.debug(f"Client {index} is now serving {ip}")

    if faster_client in class_cache:
        transfer = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logging.debug(f"Creating new ByteStreamer object for client {index}")
        transfer = ParallelTransferrer(faster_client)
        transfer.post_init()
        class_cache[faster_client] = transfer
        logging.debug(f"Created new ByteStreamer object for client {index}")
    logging.debug("before calling get_file_properties")
    try:
        file_id = await transfer.get_file_properties(msg_id)
    except FIleNotFound as e:
        return web.Response(status=404, text="File not found")
    
    file_size = file_id.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )
    until_bytes = min(until_bytes, file_size - 1)
    req_length = until_bytes - from_bytes + 1
    if not head:
        if not allow_request(ip):
            return web.Response(status=429)
        body = transfer.download(
            file_id, file_size, from_bytes, until_bytes, index, ip
        )
    else:
        body = None

    mime_type = file_id.mime_type
    file_name = file_id.file_name
    disposition = "attachment"

    if not mime_type:
        mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

    # if "video/" in mime_type or "audio/" in mime_type:
    #     disposition = "inline"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )
