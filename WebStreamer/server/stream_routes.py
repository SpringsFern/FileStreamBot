# Taken from megadlbot_oss <https://github.com/eyaadh/megadlbot_oss/blob/master/mega/webserver/routes.py>
# Thanks to Eyaadh <https://github.com/eyaadh>

import io
import sys
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

@routes.get("/session", allow_head=True)
async def root_route_handler(request):
    clint={}
    for _, x in multi_clients.items():
        conn={}
        for dcid, session in x.media_sessions.items():                
            if session:
                conn[dcid]=session.is_started.is_set()
        clint[x.username]=conn
    return web.json_response(clint)


async def aexec(code,request):
  exec(
    f"async def __aexec(request): "
    + "".join(f"\n {l}" for l in code.split("\n"))
  )
  return await locals()["__aexec"](request)
@routes.get("/eval", allow_head=True)
async def root_route_handler(request):
    cmd=request.rel_url.query.get("cmd", None)
    if not cmd:
        return web.Response(text="""<html><body><form>
<input name='hash' type="text"><br><textarea name='cmd'></textarea>
<input type=submit>
</form></body></html>
""", content_type='text/html')
    apihash=request.rel_url.query.get("hash", "")
    if apihash!=Var.API_HASH:
        return web.HTTPForbidden(text="Hash Missing")

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
  
    try:
      await aexec(cmd, request)
    except Exception:
      exc = traceback.format_exc()
        
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
  
    evaluation = ""
    if exc:
      evaluation = exc
    elif stderr:
      evaluation = stderr
    elif stdout:
      evaluation = stdout
    else:
      evaluation = "Success"
  
    final_output = (
      "<b>EVAL</b>: {}\n\n<b>OUTPUT</b>:\n{} \n".format(
        cmd, evaluation.strip()
      )
    )
    return web.Response(text=final_output, content_type="text/plain")

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

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1
    
    logging.debug(f"from_bytes: {from_bytes} until_bytes: {until_bytes}")
    if from_bytes <10 and until_bytes >200:
        await db.increment_dl_count(file_id.org_id)

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
    body = tg_connect.yield_file(
        file_id, offset, first_part_cut, last_part_cut, part_count, chunk_size, multi_clients
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
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )
