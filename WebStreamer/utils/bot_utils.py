# This file is a part of FileStreamBot

from __future__ import annotations
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.file_id import FileId, FileType, PHOTO_TYPES
from WebStreamer.utils.Translation import Language
from WebStreamer.utils.database import Database
from WebStreamer.utils.file_properties import get_media_file_size, get_name
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.vars import Var

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)

# Generate Text, Stream Link, reply_markup
async def gen_link(m: Message, _id) -> tuple[InlineKeyboardMarkup, str]:
    """Generate Text for Stream Link, Reply Text and reply_markup"""
    lang = Language(m)
    file_name = get_name(m)
    file_size = humanbytes(get_media_file_size(m))
    page_link = f"{Var.URL}watch/{_id}"
    
    stream_link = f"{Var.URL}dl/{_id}"
    Stream_Text=lang.STREAM_MSG_TEXT.format(file_name, file_size, stream_link, page_link)
    reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🖥STREAM", url=page_link), InlineKeyboardButton("Dᴏᴡɴʟᴏᴀᴅ 📥", url=stream_link)]
            ]
        )

    return reply_markup, Stream_Text

async def validate_user(message: Message, lang) -> bool:
    if Var.ALLOWED_USERS and not ((str(message.from_user.id) in Var.ALLOWED_USERS) or (message.from_user.username in Var.ALLOWED_USERS)):
        await message.reply("You are not <b>allowed to use</b> this <a href='https://github.com/EverythingSuckz/TG-FileStreamBot'>bot</a>.", quote=True)
        return False
    return True

def file_format(file_id: str | FileId) -> str:
    if isinstance(file_id, str):
        file_id=FileId.decode(file_id)
    if file_id.file_type in PHOTO_TYPES:
        return "Photo"
    elif file_id.file_type == FileType.VOICE:
        return "Voice"
    elif file_id.file_type in (FileType.VIDEO, FileType.ANIMATION, FileType.VIDEO_NOTE):
        return "Video"
    elif file_id.file_type == FileType.DOCUMENT:
        return "Document"
    elif file_id.file_type == FileType.STICKER:
        return "Sticker"
    elif file_id.file_type == FileType.AUDIO:
        return "Audio"
    else:
        return "Unknown"