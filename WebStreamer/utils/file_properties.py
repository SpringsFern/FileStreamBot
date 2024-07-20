# This file is a part of FileStreamBot

from __future__ import annotations
import logging
from datetime import datetime
from typing import List, Optional
from telethon import TelegramClient, types
from telethon.tl import types
from telethon.tl.custom.file import File
from WebStreamer.server.exceptions import FIleNotFound
from WebStreamer.utils.file_id import FileId, FileType, FileUniqueId, FileUniqueType, ThumbnailSource

async def get_file_ids(client: TelegramClient, chat_id: int, message_id: int) -> Optional[FileId]:
    message = await client.get_messages(chat_id, ids=message_id)
    if not message:
        logging.debug(f"Message with ID {message_id} not found")
        raise FIleNotFound
    file_id=get_FileId(message.media, False)
    setattr(file_id, "file_size", get_size(message.media))
    setattr(file_id, "mime_type", message.file.mime_type)
    setattr(file_id, "file_name", get_name(message.file))
    setattr(file_id, "unique_id", get_FileUniqueId(message.media))
    return file_id

def get_name(media: File | FileId) -> str:
    try:
        file_name=None
        if isinstance(media, File):
            file_name=media.name
        elif isinstance(media, FileId):
            file_name = getattr(media, "file_name", "")
        if not file_name:
            date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"{date}{media.ext}"
        return file_name
    except Exception as e:
        logging.error(e)
        logging.info(f"ErrorGettingFileName: {media}")
        return "None"

def get_FileId(file: types.MessageMediaDocument|types.MessageMediaPhoto, encode: bool= True) -> str:
    if isinstance(file, types.MessageMediaDocument):
        document: types.Document=file.document
        file_type=FileType.DOCUMENT
        for attr in document.attributes:
            if isinstance(attr, types.DocumentAttributeVideo):
                if attr.round_message:
                    file_type=FileType.VIDEO_NOTE
                else:
                    file_type=FileType.VIDEO
                break
            elif isinstance(attr, types.DocumentAttributeAnimated):
                file_type=FileType.ANIMATION
                break
            elif isinstance(attr, types.DocumentAttributeAudio):
                if attr.voice:
                    file_type=FileType.VOICE
                else:
                    file_type=FileType.AUDIO
                break
            elif isinstance(attr, types.DocumentAttributeSticker):
                file_type=FileType.STICKER
                break
        file_id = FileId(
            file_type=file_type,
            dc_id=document.dc_id,
            media_id=document.id,
            access_hash=document.access_hash,
            file_reference=document.file_reference
        )
        return file_id.encode() if encode else file_id
    elif isinstance(file, types.MessageMediaPhoto):
        photo: types.Photo=file.photo
        
        photos: List[types.PhotoSize] = []
        for p in photo.sizes:
            if isinstance(p, types.PhotoSize):
                photos.append(p)

            if isinstance(p, types.PhotoSizeProgressive):
                photos.append(
                    types.PhotoSize(
                        type=p.type,
                        w=p.w,
                        h=p.h,
                        size=max(p.sizes)
                    )
                )
        photos.sort(key=lambda p: p.size)
        main = photos[-1]

        file_type=FileType.PHOTO
        file_id = FileId(
            file_type=FileType.PHOTO,
            dc_id=photo.dc_id,
            media_id=photo.id,
            access_hash=photo.access_hash,
            file_reference=photo.file_reference,
            thumbnail_source=ThumbnailSource.THUMBNAIL,
            thumbnail_file_type=FileType.PHOTO,
            thumbnail_size=main.type,
            volume_id=0,
            local_id=0
        )
        return file_id.encode() if encode else file_id

def get_FileUniqueId(file: types.MessageMediaDocument|types.MessageMediaPhoto) -> str:
    if isinstance(file, types.MessageMediaDocument):
        document: types.Document=file.document
        return FileUniqueId(
            file_unique_type=FileUniqueType.DOCUMENT,
            media_id=document.id
        ).encode()

    elif isinstance(file, types.MessageMediaPhoto):
        photo: types.Photo=file.photo
        return FileUniqueId(
            file_unique_type=FileUniqueType.DOCUMENT,
            media_id=photo.id
        ).encode()

def get_size(file: types.MessageMediaDocument|types.MessageMediaPhoto) -> int:
    if isinstance(file, types.MessageMediaDocument):
        return getattr(file.document,"size", 0)
    elif isinstance(file, types.MessageMediaPhoto):
        photos: List[types.PhotoSize] = []
        for p in file.photo.sizes:
            if isinstance(p, types.PhotoSize):
                photos.append(p)

            if isinstance(p, types.PhotoSizeProgressive):
                photos.append(
                    types.PhotoSize(
                        type=p.type,
                        w=p.w,
                        h=p.h,
                        size=max(p.sizes)
                    )
                )
        photos.sort(key=lambda p: p.size)
        main = photos[-1]
        return main.size