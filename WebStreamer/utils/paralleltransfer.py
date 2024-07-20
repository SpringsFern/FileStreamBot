# This file is a part of FileStreamBot
#
# Copyright (C) 2019 Tulir Asokan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import Union, AsyncGenerator, AsyncContextManager, Dict, Optional, List
from contextlib import asynccontextmanager
from dataclasses import dataclass
import logging
import asyncio
import math

from telethon import TelegramClient
from telethon.crypto import AuthKey
from telethon.network import MTProtoSender
from telethon.tl.functions.auth import ExportAuthorizationRequest, ImportAuthorizationRequest
from telethon.tl.functions.upload import GetFileRequest
from telethon.tl.types import (Document, InputFileLocation, InputDocumentFileLocation,
                               InputPhotoFileLocation, InputPeerPhotoFileLocation, DcOption,
                               InputPeerChat, InputPeerUser, InputPeerChannel)
from telethon.errors import DcIdInvalidError

from WebStreamer.utils.utils import decrement_counter, increment_counter

TypeLocation = Union[Document, InputDocumentFileLocation, InputPeerPhotoFileLocation,
                     InputFileLocation, InputPhotoFileLocation]

from WebStreamer.utils.file_id import FileId, FileType, ThumbnailSource
from WebStreamer.utils.file_properties import get_file_ids
from WebStreamer.vars import Var
from WebStreamer.bot import work_loads

root_log = logging.getLogger(__name__)

if Var.CONNECTION_LIMIT > 25:
    root_log.warning("The connection limit should not be set above 25 to avoid"
                     " infinite disconnect/reconnect loops")


@dataclass
class Connection:
    log: logging.Logger
    sender: MTProtoSender
    lock: asyncio.Lock
    users: int = 0


class DCConnectionManager:
    log: logging.Logger
    client: TelegramClient
    loop: asyncio.AbstractEventLoop

    dc_id: int
    dc: Optional[DcOption]
    auth_key: Optional[AuthKey]
    connections: List[Connection]

    _list_lock: asyncio.Lock

    def __init__(self, client: TelegramClient, dc_id: int) -> None:
        self.log = root_log.getChild(f"dc{dc_id}")
        self.client = client
        self.dc_id = dc_id
        self.auth_key = None
        self.connections = []
        self._list_lock = asyncio.Lock()
        self.loop = client.loop
        self.dc = None

    async def _new_connection(self) -> Connection:
        if not self.dc:
            self.dc = await self.client._get_dc(self.dc_id)
        sender = MTProtoSender(self.auth_key, loggers=self.client._log)
        index = len(self.connections) + 1
        conn = Connection(sender=sender, log=self.log.getChild(f"conn{index}"), lock=asyncio.Lock())
        self.connections.append(conn)
        async with conn.lock:
            conn.log.info("Connecting...")
            connection_info = self.client._connection(self.dc.ip_address, self.dc.port, self.dc.id,
                                                      loggers=self.client._log,
                                                      proxy=self.client._proxy)
            await sender.connect(connection_info)
            if not self.auth_key:
                await self._export_auth_key(conn)
            return conn

    async def _export_auth_key(self, conn: Connection) -> None:
        self.log.info(f"Exporting auth to DC {self.dc.id}"
                      f" (main client is in {self.client.session.dc_id})")
        try:
            auth = await self.client(ExportAuthorizationRequest(self.dc.id))
        except DcIdInvalidError:
            self.log.debug("Got DcIdInvalidError")
            self.auth_key = self.client.session.auth_key
            conn.sender.auth_key = self.auth_key
            return
        req = self.client._init_with(ImportAuthorizationRequest(
            id=auth.id, bytes=auth.bytes
        ))
        await conn.sender.send(req)
        self.auth_key = conn.sender.auth_key

    async def _next_connection(self) -> Connection:
        best_conn: Optional[Connection] = None
        for conn in self.connections:
            if not best_conn or conn.users < best_conn.users:
                best_conn = conn
        if (not best_conn or best_conn.users > 0) and len(self.connections) < Var.CONNECTION_LIMIT:
            best_conn = await self._new_connection()
        return best_conn

    @asynccontextmanager
    async def get_connection(self) -> AsyncContextManager[Connection]:
        async with self._list_lock:
            conn: Connection = await asyncio.shield(self._next_connection())
            # The connection is locked so reconnections don't stack
            async with conn.lock:
                conn.users += 1
        try:
            yield conn
        finally:
            conn.users -= 1


class ParallelTransferrer:
    log: logging.Logger = logging.getLogger(__name__)
    client: TelegramClient
    loop: asyncio.AbstractEventLoop

    dc_managers: Dict[int, DCConnectionManager]

    _counter: int

    def __init__(self, client: TelegramClient) -> None:
        self.client = client
        self.loop = self.client.loop
        self._counter = 0
        self.dc_managers = {
            1: DCConnectionManager(client, 1),
            2: DCConnectionManager(client, 2),
            3: DCConnectionManager(client, 3),
            4: DCConnectionManager(client, 4),
            5: DCConnectionManager(client, 5),
        }
        self.clean_timer = 30 * 60
        self.cached_file_ids: Dict[int, FileId] = {}
        asyncio.create_task(self.clean_cache())

    async def get_file_properties(self, message_id: int) -> FileId:
        """
        Returns the properties of a media of a specific message in a FIleId class.
        if the properties are cached, then it'll return the cached results.
        or it'll generate the properties from the Message ID and cache them.
        """
        if message_id not in self.cached_file_ids:
            await self.generate_file_properties(message_id)
            logging.debug(f"Cached file properties for message with ID {message_id}")
        return self.cached_file_ids[message_id]
    
    async def generate_file_properties(self, message_id: int) -> FileId:
        """
        Generates the properties of a media file on a specific message.
        returns ths properties in a FIleId class.
        """
        file_id = await get_file_ids(self.client, Var.BIN_CHANNEL, message_id)
        logging.debug(f"Generated file ID and Unique ID for message with ID {message_id}")
        self.cached_file_ids[message_id] = file_id
        logging.debug(f"Cached media message with ID {message_id}")
    
    @staticmethod
    def get_location(file_id: FileId) -> TypeLocation:
        """
        Returns the file location for the media file.
        """
        file_type = file_id.file_type

        if file_type == FileType.CHAT_PHOTO:
            if file_id.chat_id > 0:
                peer = InputPeerUser(
                    user_id=file_id.chat_id, access_hash=file_id.chat_access_hash
                )
            else:
                if file_id.chat_access_hash == 0:
                    peer = InputPeerChat(chat_id=-file_id.chat_id)
                else:
                    peer = InputPeerChannel(
                        channel_id=-1000000000000 - file_id.chat_id,
                        access_hash=file_id.chat_access_hash,
                    )

            location = InputPeerPhotoFileLocation(
                peer=peer,
                volume_id=file_id.volume_id,
                local_id=file_id.local_id,
                big=file_id.thumbnail_source == ThumbnailSource.CHAT_PHOTO_BIG,
            )
        elif file_type == FileType.PHOTO:
            location = InputPhotoFileLocation(
                id=file_id.media_id,
                access_hash=file_id.access_hash,
                file_reference=file_id.file_reference,
                thumb_size=file_id.thumbnail_size,
            )
        else:
            location = InputDocumentFileLocation(
                id=file_id.media_id,
                access_hash=file_id.access_hash,
                file_reference=file_id.file_reference,
                thumb_size=file_id.thumbnail_size,
            )
        return location

    def post_init(self) -> None:
        self.dc_managers[self.client.session.dc_id].auth_key = self.client.session.auth_key

    @property
    def next_index(self) -> int:
        self._counter += 1
        return self._counter

    async def _int_download(self, request: GetFileRequest, dc_id: int,first_part_cut: int,
        last_part_cut: int, part_count: int, chunk_size: int,
        last_part: int, total_parts: int, index: int, ip: str) -> AsyncGenerator[bytes, None]:
        log = self.log
        try:
            increment_counter(ip)
            work_loads[index] += 1
            current_part = 1
            dcm = self.dc_managers[dc_id]
            async with dcm.get_connection() as conn:
                log = conn.log
                while current_part <= part_count:
                    result = await conn.sender.send(request)
                    request.offset += chunk_size
                    if not result.bytes:
                        break
                    elif part_count == 1:
                        yield result.bytes[first_part_cut:last_part_cut]
                    elif current_part == 1:
                        yield result.bytes[first_part_cut:]
                    elif current_part == part_count:
                        yield result.bytes[:last_part_cut]
                    else:
                        yield result.bytes
                    log.debug(f"Part {current_part}/{last_part} (total {total_parts}) downloaded")
                    current_part += 1
                log.debug("Parallel download finished")
        except (GeneratorExit, StopAsyncIteration, asyncio.CancelledError):
            log.debug("Parallel download interrupted")
            raise
        except Exception:
            log.debug("Parallel download errored", exc_info=True)
        finally:
            logging.debug(f"Finished yielding file with {current_part} parts.")
            work_loads[index] -= 1
            decrement_counter(ip)

    def download(self, file_id: FileId, file_size: int, from_bytes: int, until_bytes: int, index: int, ip: str
        ) -> AsyncGenerator[bytes, None]:
        dc_id = file_id.dc_id
        location=self.get_location(file_id)

        chunk_size = Var.CHUNK_SIZE
        offset = from_bytes - (from_bytes % chunk_size)
        first_part_cut = from_bytes - offset
        first_part = math.floor(offset / chunk_size)
        last_part_cut = until_bytes % chunk_size + 1
        last_part = math.ceil(until_bytes / chunk_size)
        part_count = last_part - first_part
        total_parts = math.ceil(file_size / chunk_size)

        self.log.debug(f"Starting parallel download: chunks {first_part}-{last_part}"
                       f" of {part_count} {location!s}")
        request = GetFileRequest(location, offset=offset, limit=chunk_size)

        return self._int_download(request, dc_id, first_part_cut, last_part_cut,
            part_count, chunk_size, last_part, total_parts, index, ip)

    async def clean_cache(self) -> None:
        """
        function to clean the cache to reduce memory usage
        """
        while True:
            await asyncio.sleep(self.clean_timer)
            self.cached_file_ids.clear()
            logging.debug("Cleaned the cache")