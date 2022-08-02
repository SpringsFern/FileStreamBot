# This file is a part of FileStreamBot

import random
from WebStreamer.bot import StreamBot
from WebStreamer.utils.file_properties import gen_link, get_media_file_unique_id
from WebStreamer.vars import Var
from WebStreamer.utils.Translation import Language, BUTTON
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageDeleteForbidden

@StreamBot.on_callback_query()
async def cb_data(bot, update: CallbackQuery):
    # lang = getattr(Language, update.from_user.language_code)
    lang = getattr(Language, "en")
    if update.data == "home":
        await update.message.edit_text(
            text=lang.START_TEXT.format(update.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=BUTTON.START_BUTTONS
        )
    elif update.data == "help":
        await update.message.edit_text(
            text=lang.HELP_TEXT.format(Var.UPDATES_CHANNEL),
            disable_web_page_preview=True,
            reply_markup=BUTTON.HELP_BUTTONS
        )
    elif update.data == "about":
        await update.message.edit_text(
            text=lang.ABOUT_TEXT,
            disable_web_page_preview=True,
            reply_markup=BUTTON.ABOUT_BUTTONS
        )
    elif update.data == "close":
        await update.message.delete()
    else:
        await update.message.delete()