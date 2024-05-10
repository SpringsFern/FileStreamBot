# Taken from megadlbot_oss <https://github.com/eyaadh/megadlbot_oss/blob/master/mega/webserver/routes.py>
# Thanks to Eyaadh <https://github.com/eyaadh>

import time
import math
import logging
import mimetypes
import traceback
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from WebStreamer.bot import multi_clients, work_loads, StreamBot
from WebStreamer.vars import Var
from WebStreamer.server.exceptions import FIleNotFound, InvalidHash, FIleExpired
from WebStreamer import utils, StartTime, __version__
from WebStreamer.utils.bot_utils import db
routes = web.RouteTableDef()

@routes.get("/status", allow_head=True)
async def root_route_handler(request):
    return web.json_response(
        {
            "server_status": "running",
            "uptime": utils.get_readable_time(time.time() - StartTime),
            "telegram_bot": "@" + StreamBot.username,
            "connected_bots": len(multi_clients),
            "loads": dict(
                (multi_clients[c].username if request.rel_url.query.get("id") else "bot" +str(c), l)
                for c,  l in work_loads.items()
                # for c, (_, l) in enumerate(
            #         sorted(work_loads.items(), key=lambda x: x[1], reverse=True)
            #     )
            ),
            "version": __version__,
        }
    )

@routes.get("/dl/{path}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        return await media_streamer(request, path)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except FIleExpired as e:
        raise web.HTTPNotFound(text=e.message, content_type='text/html') 
    except Exception as e:
        traceback.print_exc()
        logging.critical(e.with_traceback(None))
        logging.debug(traceback.format_exc())
        raise web.HTTPInternalServerError(text=str(e))

class_cache = {}
async def media_streamer(request: web.Request, db_id: str):
    if not utils.tg_connect:
        logging.debug(f"Creating new ByteStreamer object")
        utils.tg_connect=utils.ByteStreamer()
    else:
        logging.debug(f"Using cached ByteStreamer object")
    tg_connect=utils.tg_connect
    range_header = request.headers.get("Range", 0)
    
    # index = min(work_loads, key=work_loads.get)

    logging.debug("before calling get_file_properties")
    file_id = await tg_connect.get_file_properties(db_id, multi_clients)
    logging.debug("after calling get_file_properties")
    
    if Var.MULTI_CLIENT:
        logging.info(f"Client {file_id.index} is now serving {request.headers.get('X-FORWARDED-FOR',request.remote)}")
    
    file_size = file_id.file_size

    try:
        offset = request.http_range.start or 0
        limit = request.http_range.stop or file_size
        if (limit > file_size) or (offset < 0) or (limit < offset):
            raise ValueError("range not in acceptable format")
    except ValueError:
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    body = tg_connect.yield_file(
        file_id, offset, limit, multi_clients
    )

    mime_type = file_id.mime_type
    file_name = utils.get_name(file_id)
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
            "Content-Range": f"bytes {offset}-{limit}/{file_size}",
            "Content-Length": str(limit - offset),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )
