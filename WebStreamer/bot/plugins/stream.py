# This file is a part of FileStreamBot


import asyncio
from WebStreamer.utils.Translation import Language
from WebStreamer.bot import StreamBot, multi_clients
from WebStreamer.utils.bot_utils import gen_link, validate_user
from WebStreamer.utils.database import Database
from WebStreamer.utils.file_properties import get_file_ids, get_file_info
from WebStreamer.vars import Var
from pyrogram import filters, Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from pyrogram.enums.parse_mode import ParseMode
db = Database(Var.DATABASE_URL, Var.SESSION_NAME)

@StreamBot.on_message(
    filters.private
    & (
        filters.document
        | filters.video
        | filters.audio
        | filters.animation
        | filters.voice
        | filters.video_note
        | filters.photo
        | filters.sticker
    ),
    group=4,
)
async def private_receive_handler(bot: Client, message: Message):
    lang = Language(message)
    if not await validate_user(message, lang):
        return
    try:
        ptype=await db.link_available(message.from_user.id)
        if not (ptype):
            return await message.reply_text(lang.LINK_LIMIT_EXCEEDED)

        inserted_id=await db.add_file(get_file_info(message))
        await get_file_ids(False, inserted_id, multi_clients)
        reply_markup, Stream_Text = await gen_link(m=message, _id=inserted_id, name=[StreamBot.username, StreamBot.fname])
        await message.reply_text(
            text=Stream_Text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            quote=True
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.value)}s")
        await asyncio.sleep(e.value)
        await bot.send_message(chat_id=Var.BIN_CHANNEL, text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.value)}s from [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n\n**𝚄𝚜𝚎𝚛 𝙸𝙳 :** `{str(message.from_user.id)}`", disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)