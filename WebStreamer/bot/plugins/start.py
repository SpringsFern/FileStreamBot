# This file is a part of FileStreamBot

import json
import logging
import re
import math
import requests
from WebStreamer import __version__
from WebStreamer.bot import StreamBot
from WebStreamer.server.exceptions import FIleNotFound
from WebStreamer.utils.bot_utils import is_user_accepted_tos, is_user_banned, is_user_exist, is_user_joined
from WebStreamer.vars import Var
from WebStreamer.utils.database import Database
from WebStreamer.utils.Translation import Language, BUTTON
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.enums.chat_action import ChatAction

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)
url_pattern = re.compile(r'https?://dl\.tgxlink\.eu\.org/dl/([0-9a-fA-F]{24})')

@StreamBot.on_message(filters.command('start') & filters.private)
async def start(bot: Client, message: Message):
    lang = Language(message)
    # Check The User is Banned or Not
    if await is_user_banned(message, lang):
        return
    await is_user_exist(bot, message)
    if Var.TOS:
        if not await is_user_accepted_tos(message):
            return
    # usr_cmd = message.text.split("_")[-1]
    if Var.FORCE_UPDATES_CHANNEL:
        if not is_user_joined(bot,message,lang):
            return
    usr_cmd = message.text.split(" ")
    if usr_cmd[-1] == "/start":
        await message.reply_text(
            text=lang.START_TEXT.format(message.from_user.mention),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=BUTTON.START_BUTTONS
            )
    else:
        try:
            _id, file_unique_id=(usr_cmd[-1]).split("_")
            myfile = await db.get_file(_id)
            if myfile['file_unique_id'] == file_unique_id:
                await message.reply_cached_media(myfile['file_id'])
            else:
                await message.reply_text("File not found")
        except FIleNotFound as e:
            return message.reply_text(e)
        except Exception as e:
            logging.error(e)
            await message.reply_text("Something Went Wrong")


@StreamBot.on_message(filters.private & filters.command(["about"]))
async def start(bot, message):
    lang = Language(message)
    if await is_user_banned(message, lang):
        return
    await is_user_exist(bot, message)
    if Var.TOS:
        if not await is_user_accepted_tos(message):
            return
    if Var.FORCE_UPDATES_CHANNEL:
        if not await is_user_joined(bot,message,lang):
            return
    await message.reply_text(
        text=lang.ABOUT_TEXT.format(__version__),
        disable_web_page_preview=True,
        reply_markup=BUTTON.ABOUT_BUTTONS
    )


@StreamBot.on_message((filters.command('help')) & filters.private)
async def help_handler(bot, message):
    lang = Language(message)
    # Check The User is Banned or Not
    if await is_user_banned(message, lang):
        return
    await is_user_exist(bot, message)
    if Var.TOS:
        if not await is_user_accepted_tos(message):
            return
    if Var.FORCE_UPDATES_CHANNEL:
        if not await is_user_joined(bot,message,lang):
            return
    await message.reply_text(
        text=lang.HELP_TEXT.format(Var.UPDATES_CHANNEL),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=BUTTON.HELP_BUTTONS
        )

# -----------------------------Only for me you can remove below line -------------------------------------------------------

@StreamBot.on_message(filters.command('getid') & filters.private)
async def start(bot, message):
    await message.reply_text(
        text=f"Your ID is: `{message.chat.id}`"
    )

# ---------------------------------------------------------------------------------------------------

@StreamBot.on_message(filters.command('myfiles') & filters.private)
async def my_files(bot: Client, message: Message):
    user_files, total_files=await db.find_files(message.from_user.id, [1,10])

    file_list=[]
    async for x in user_files:
        file_list.append([InlineKeyboardButton(x["file_name"], callback_data=f"myfile_{x['_id']}_{1}")])
    if total_files > 10:
        file_list.append(
            [
                InlineKeyboardButton("<<", callback_data="N/A"),
                InlineKeyboardButton(f"1/{math.ceil(total_files/10)}", callback_data="N/A"),
                InlineKeyboardButton(">>", callback_data="userfiles_2")
            ]
    )
    if not file_list:
        file_list.append([InlineKeyboardButton("Empty", callback_data="N/A")])
    await message.reply_photo(photo=Var.IMAGE_FILEID,
        caption="Total files: {}".format(total_files),
        reply_markup=InlineKeyboardMarkup(file_list))

@StreamBot.on_message(filters.command('tos') & filters.private)
async def tos(bot: Client, message: Message):
    if not Var.TOS:
        await message.reply_text("This bot does not currently have any terms of service.")
        return
    if (await is_user_accepted_tos(message)):
        await message.reply_text(
            Var.TOS,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ I accepted the TOS", callback_data="N/A")]])
            )
    else:
        await message.reply_text(
            Var.TOS,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("I accept the TOS", callback_data=f"accepttos_{message.from_user.id}")]])
            )

@StreamBot.on_message(filters.text & filters.private & filters.regex(url_pattern))
async def file_from_link(bot: Client, message: Message):

    match = url_pattern.search(message.text)

    object_id = match.group(1)
    try:
        myfile = await db.get_file(object_id)
    except FIleNotFound as e:
        return message.reply_text(e)
    params={
            "api": Var.TN_API,
            "url": f"https://t.me/{StreamBot.username}?start={myfile['_id']}_{myfile['file_unique_id']}",
            "alias": f"{str(message.id)}_{message.from_user.id}"
        }
    shortned_url=(requests.get("https://tnlinks.in/api",params=params)).json()
    if shortned_url['status'] == "success":
        await message.reply_text("[Click here to get file]({})".format(shortned_url['shortenedUrl']))
    else:
        await message.reply_text("Please try again later")

@StreamBot.on_message(filters.command('info') & filters.private)
async def tos(bot: Client, message: Message):
    i_cmd=message.text.split()
    if (message.from_user.id == Var.OWNER_ID) and (len(i_cmd) > 1):
        user = await db.get_user(int(i_cmd[2]))
        files=await db.total_files(int(i_cmd[2]))
    else:
        user = await db.get_user(message.from_user.id)
        files=await db.total_files(message.from_user.id)
    links="N/A"
    if user.get("Plan") == "Free":
        links=20-user.get("Links")
    await message.reply_text(f"""User ID: <code>{message.from_user.id}</code>
Plan: <code>{user.get("Plan")}</code>
Links Used: <code>{files}</code>
Links Left: <code>{links}<code>

For Additional Links Contact @DeekshithSH
Note: This Plan Can be Changed at any time""")

@StreamBot.on_message(filters.command('links') & filters.private)
async def link_list(bot: Client, message: Message):
    await message.reply_chat_action(ChatAction.TYPING)
    user_files, total_files=await db.find_files(message.from_user.id, [1,10])
    list_type=message.text.split()[-1]
    list_type=list_type if list_type != "/links" else None
    if list_type=="json":
        file_list={}
    else:
        file_list=""
    async for x in user_files:
        if list_type == "json":
            file_list[x["file_name"]]=Var.URL+"dl/"+str(x["_id"])
        elif list_type == "link":
            file_list+=f'\n\n{x["file_name"]} : {Var.URL+"dl/"+str(x["_id"])}'
        else:
            file_list+=f'\n<a href={Var.URL+"dl/"+str(x["_id"])}>{x["file_name"]}</a>'

    if isinstance(file_list, dict):
        file_list=json.dumps(file_list)
    await message.reply_text(file_list, disable_web_page_preview=True)
    await message.reply_chat_action(ChatAction.CANCEL)