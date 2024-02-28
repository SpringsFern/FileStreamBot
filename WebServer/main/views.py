import datetime
import logging

import aiohttp_jinja2
from aiohttp import web, web_exceptions
from bson.objectid import ObjectId
from bson.errors import InvalidId

from WebServer.utils.database import Database
from WebServer.utils.vars import Var
from WebServer.utils.human_readable import humanbytes

db=Database(Var.DATABASE_URL, Var.SESSION_NAME)

@aiohttp_jinja2.template('dl.html')
async def index(request: web.Request):
    return {
        "hidee": "",
        "hides": "",
        "tag": "video",
        "source_link": "https://download.blender.org/peach/trailer/trailer_1080p.ogg",
        "download_link": "https://download.blender.org/peach/trailer/trailer_1080p.ogg",
        "file_name": "Big Buck Bunny Trailer",
        "file_size": "26MB",
        "user_id": "849816969",
        "time": "2023-10-15 12:25 PM"
    }

async def status(request: web.Request):
    return web.HTTPOk()

@aiohttp_jinja2.template('dl.html')
async def FileHandler(request: web.Request):
    logging.debug("FileHandler Begining")
    try: 
        objid=ObjectId(request.match_info["ObjectID"])
    except InvalidId:
        raise web_exceptions.HTTPClientError(text="Invalid ObjectID")
    dl_link=await db.create_link(objid)
    file=await db.get_file(objid)
    if not file:
        raise web_exceptions.HTTPNotFound
    logging.debug("Generated DL Link")

    file_type=file["mime_type"].split("/")[0]
    player=None
    if file_type in ["audio", "video"]:
        player=file_type

    return {
        "hides": "" if player else "<!--",
        "hidee": "" if player else "-->",
        "tag": player,
        "source_link": dl_link if player else None,
        "download_link": dl_link,
        "file_name": file["file_name"],
        "file_size": humanbytes(file["file_size"]),
        "user_id": file["user_id"],
        "time": datetime.datetime.fromtimestamp(file["time"])
    }