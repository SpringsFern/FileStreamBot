# This file is a part of FileStreamBot

import math
from WebStreamer import __version__
from WebStreamer.bot import StreamBot
from WebStreamer.server.exceptions import FIleNotFound
from WebStreamer.utils.bot_utils import is_user_accepted_tos, validate_user
from WebStreamer.vars import Var
from WebStreamer.utils.database import Database
from WebStreamer.utils.Translation import Language, BUTTON
from telethon.events import filters, NewMessage
from telethon.types import User
from telethon.types.buttons import Callback

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)

@StreamBot.on(NewMessage, filters.Command('/start') & filters.ChatType(User))
async def start(event: NewMessage):
    # event.
    lang = Language()
    if not await validate_user(event, lang):
        return
    # usr_cmd = message.text.split(" ")
    # if usr_cmd[-1] == "/start":
    await event.reply(
        text=lang.START_TEXT.format(f"[{event.chat.name}](tg://user?id={event.chat.id})"),
        markdown=True,
        html=True,
        link_preview=True,
        buttons=BUTTON.START_BUTTONS
        )

@StreamBot.on(NewMessage, filters.Command('/about') & filters.ChatType(User))
async def about(event: NewMessage):
    lang = Language()
    if not await validate_user(event, lang):
        return
    await event.reply(
        text=lang.ABOUT_TEXT.format(__version__),
        link_preview=True,
        reply_markup=BUTTON.ABOUT_BUTTONS
    )


@StreamBot.on(NewMessage, filters.Command('/help') & filters.ChatType(User))
async def help_handler(event: NewMessage):
    lang = Language()
    if not await validate_user(event, lang):
        return
    await event.reply(
        text=lang.HELP_TEXT.format(Var.UPDATES_CHANNEL),
        html=True,
        disable_web_page_preview=True,
        reply_markup=BUTTON.HELP_BUTTONS
        )

# ---------------------------------------------------------------------------------------------------

@StreamBot.on(NewMessage, filters.Command('/myfiles') & filters.ChatType(User))
async def my_files(event: NewMessage):
    if not await validate_user(event):
        return
    user_files, total_files=await db.find_files(event.chat.id, [1,10])

    file_list=[]
    async for x in user_files:
        file_list.append([Callback(x["file_name"], f"myfile_{x['_id']}_{1}".encode('utf-8'))])
    if total_files > 10:
        file_list.append(
            [
                Callback("<<", b"N/A"),
                Callback(f"1/{math.ceil(total_files/10)}", b"N/A"),
                Callback(">>", b"userfiles_2")
            ]
    )
    if not file_list:
        file_list.append([Callback("Empty", b"N/A")])
    await event.client.send_photo(chat=event.chat.ref,
        photo=Var.IMAGE_FILEID,
        caption="Total files: {}".format(total_files),
        buttons=file_list)

@StreamBot.on(NewMessage, filters.Command('/tos') & filters.ChatType(User))
async def tos_handler(event: NewMessage):
    if not Var.TOS:
        await event.reply("This bot does not have any terms of service.")
        return
    if (await is_user_accepted_tos(event)):
        await event.reply(
            Var.TOS,
            buttons=[[Callback("✅ I accepted the TOS", b"N/A")]]
        )

@StreamBot.on(NewMessage, filters.Command('/getfile') & filters.ChatType(User))
async def getfile(event: NewMessage):
    if not await validate_user(event):
        return
    usr_cmd=event.text.split()
    if len(usr_cmd) < 2:
        return await event.reply("Invalid Format\nUsage: `/getfile _id`")
    for x in usr_cmd[1:]:
        try:
            myfile = await db.get_file(x)
            # ToDo
            # await event.client(myfile['file_id'])
        except FIleNotFound:
            await event.reply(f"{x} :File Not Found")