# This file is a part of FileStreamBot

import math
from WebStreamer import __version__
from WebStreamer.bot import StreamBot
from WebStreamer.utils.bot_utils import is_user_accepted_tos, is_user_banned, is_user_exist, is_user_joined
from WebStreamer.vars import Var
from WebStreamer.utils.database import Database
from WebStreamer.utils.Translation import Language, BUTTON
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums.parse_mode import ParseMode

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)

@StreamBot.on_message(filters.command('start') & filters.private)
async def start(bot, message):
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
    await message.reply_text(
        text=lang.START_TEXT.format(message.from_user.mention),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=BUTTON.START_BUTTONS
        )


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