# This file is a part of FileStreamBot

import aiohttp
import aiofiles
import urllib.parse
from WebStreamer.vars import Var
from WebStreamer.utils.database import Database
from WebStreamer.utils.human_readable import humanbytes
db = Database(Var.DATABASE_URL, Var.SESSION_NAME)

async def render_page(db_id):
    file_data=await db.get_file(db_id)
    src = urllib.parse.urljoin(Var.URL, f'dl/{file_data["_id"]}')
    if str((file_data['mime_type']).split('/')[0].strip()) == 'video':
        async with aiofiles.open('WebStreamer/template/req.html') as r:
            heading = 'Watch {}'.format(file_data['file_name'])
            tag = (file_data['mime_type']).split('/')[0].strip()
            html = (await r.read()).replace('tag', tag) % (heading, file_data['file_name'], src)
    elif str((file_data['mime_type']).split('/')[0].strip()) == 'audio':
        async with aiofiles.open('WebStreamer/template/req.html') as r:
            heading = 'Listen {}'.format(file_data['file_name'])
            tag = (file_data['mime_type']).split('/')[0].strip()
            html = (await r.read()).replace('tag', tag) % (heading, file_data['file_name'], src)
    else:
        async with aiofiles.open('WebStreamer/template/dl.html') as r:
            async with aiohttp.ClientSession() as s:
                async with s.get(src) as u:
                    heading = 'Download {}'.format(file_data['file_name'])
                    file_size = humanbytes(int(u.headers.get('Content-Length')))
                    html = (await r.read()) % (heading, file_data['file_name'], src, file_size)
    return html
