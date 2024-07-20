import asyncio
import logging
import pathlib
import platform
import re
from typing import Type, Union

from telethon.tl.alltlobjects import LAYER
from telethon import TelegramClient
from telethon.tl import functions
from telethon.network import Connection, ConnectionTcpFull
from telethon.sessions import Session


class TLClient(TelegramClient):
    def __init__(
            self: 'TelegramClient',
            session: 'Union[str, pathlib.Path, Session]',
            api_id: int,
            api_hash: str,
            *,
            connection: 'Type[Connection]' = ConnectionTcpFull,
            use_ipv6: bool = False,
            proxy: Union[tuple, dict] = None,
            local_addr: Union[str, tuple] = None,
            timeout: int = 10,
            request_retries: int = 5,
            connection_retries: int = 5,
            retry_delay: int = 1,
            auto_reconnect: bool = True,
            sequential_updates: bool = False,
            flood_sleep_threshold: int = 60,
            raise_last_call_error: bool = False,
            device_model: str = None,
            system_version: str = None,
            app_version: str = None,
            lang_code: str = 'en',
            system_lang_code: str = 'en',
            loop: asyncio.AbstractEventLoop = None,
            base_logger: Union[str, logging.Logger] = None,
            receive_updates: bool = True,
            catch_up: bool = False,
            entity_cache_limit: int = 5000
        ):
        super().__init__(
            session,
            api_id,
            api_hash,
            connection=connection,
            use_ipv6=use_ipv6,
            proxy=proxy,
            local_addr=local_addr,
            timeout=timeout,
            request_retries=request_retries,
            connection_retries=connection_retries,
            retry_delay=retry_delay,
            auto_reconnect=auto_reconnect,
            sequential_updates=sequential_updates,
            flood_sleep_threshold=flood_sleep_threshold,
            raise_last_call_error=raise_last_call_error,
            device_model=device_model,
            system_version=system_version,
            app_version=app_version,
            lang_code=lang_code,
            system_lang_code=system_lang_code,
            loop=loop,
            base_logger=base_logger,
            receive_updates=receive_updates,
            catch_up=catch_up,
            entity_cache_limit=entity_cache_limit)

        system = platform.uname()
        if system.machine in ('x86_64', 'AMD64'):
            default_device_model = 'PC 64bit'
        elif system.machine in ('i386','i686','x86'):
            default_device_model = 'PC 32bit'
        else:
            default_device_model = system.machine
        default_system_version = re.sub(r'-.+','',system.release)
        self._init_with = lambda x: functions.InvokeWithLayerRequest(
            LAYER, functions.InitConnectionRequest(
                api_id=self.api_id,
                device_model=default_device_model,
                system_version=system_version or default_system_version or '1.0',
                app_version=app_version or self.__version__,
                lang_code=lang_code,
                system_lang_code=system_lang_code,
                lang_pack='',  # "langPacks are for official apps only"
                query=x,
                proxy=None
            )
        )
    
    async def startup(self):
        config = await self(functions.help.GetConfigRequest())
        for option in config.dc_options:
            if option.ip_address == self.session.server_address:
                if self.session.dc_id != option.id:
                    logging.warning(f"Fixed DC ID in session from {self.session.dc_id} to {option.id}")
                self.session.set_dc(option.id, option.ip_address, option.port)
                self.session.save()
                break
        # transfer.post_init()