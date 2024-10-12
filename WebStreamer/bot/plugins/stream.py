# This file is a part of FileStreamBot

import logging
import urllib.parse
from time import time
from WebStreamer.bot import StreamBot
from telethon import Button, errors
from telethon.events import NewMessage
from telethon.extensions import html
from WebStreamer.utils.Translation import Language
from WebStreamer.utils.utils import validate_user
from WebStreamer.utils.file_properties import get_name, get_size
from WebStreamer.utils.utils import humanbytes
from WebStreamer.vars import Var

@StreamBot.on(NewMessage(func=lambda e: True if e.message.file else False))
async def private_receive_handler(event: NewMessage.Event):
    if not await validate_user(event):
        return
    try:
        # if not event.message.file:
        #     logging.info(f"MediaNotFound: {event.stringify()}")
        #     return
        log_msg=await event.message.forward_to(Var.BIN_CHANNEL)
        lang = Language(event)
        file_name = get_name(event.message.file)
        file_size = humanbytes(get_size(event.message.media))

        if Var.CUSTOM_URL:
            stream_link=Var.LINK_TEMPLATE.format_map({
                "url": Var.CUSTOM_URL,
                "name": urllib.parse.quote(file_name),
                "size": get_size(event.message.media),
                "id": log_msg.id,
                "mime": urllib.parse.quote(log_msg.file.mime_type),
                "time": int(time())
            })
        else:
            stream_link = f"{Var.URL}dl/{log_msg.id}/{urllib.parse.quote(get_name(event.message.file))}"

        await event.message.reply(
            message=lang.STREAM_MSG_TEXT.format_map({
                "name": file_name,
                "size": file_size,
                "link": stream_link,
                "username": StreamBot.username,
                "firstname": StreamBot.fname
                }),
            link_preview=False,
            buttons=[
            [Button.url("Dᴏᴡɴʟᴏᴀᴅ 📥", url=stream_link)]
            ],
            parse_mode=html
        )
    except errors.FloodWaitError as e:
        logging.error(e)