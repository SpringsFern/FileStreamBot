# This file is a part of FileStreamBot

from telethon.extensions import html
from WebStreamer import __version__
from WebStreamer.bot import StreamBot
from WebStreamer.utils.utils import validate_user
from WebStreamer.vars import Var
from WebStreamer.utils.Translation import Language, BUTTON
from telethon.events import NewMessage

@StreamBot.on(NewMessage(incoming=True,pattern=r"^\/start*"))
async def start(event: NewMessage.Event):
    lang = Language()
    if not await validate_user(event):
        return
    await event.message.reply(
        message=lang.START_TEXT.format(event.chat_id, event.chat.first_name),
        link_preview=False,
        buttons=BUTTON.START_BUTTONS,
        parse_mode=html
    )

@StreamBot.on(NewMessage(incoming=True,pattern=r"^\/about*"))
async def about(event: NewMessage.Event):
    lang = Language()
    if not await validate_user(event):
        return
    await event.message.reply(
        message=lang.ABOUT_TEXT.format(__version__),
        link_preview=False,
        buttons=BUTTON.ABOUT_BUTTONS,
        parse_mode=html
    )


@StreamBot.on(NewMessage(incoming=True,pattern=r"^\/help*"))
async def help_handler(event: NewMessage.Event):
    lang = Language()
    if not await validate_user(event):
        return
    await event.message.reply(
        message=lang.HELP_TEXT.format(Var.UPDATES_CHANNEL),
        buttons=BUTTON.HELP_BUTTONS,
        parse_mode=html,
        link_preview=False
        )
