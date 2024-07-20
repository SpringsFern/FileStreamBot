# This file is a part of FileStreamBot

import asyncio
import logging
from os import environ
from ..vars import Var
from .helper import TLClient
from telethon.sessions import MemorySession
from . import multi_clients, work_loads, StreamBot


async def initialize_clients():
    all_tokens = dict(
        (c + 1, t)
        for c, (_, t) in enumerate(
            filter(
                lambda n: n[0].startswith("MULTI_TOKEN"), sorted(environ.items())
            )
        )
    )
    if not all_tokens:
        multi_clients[0] = StreamBot
        work_loads[0] = 0
        print("No additional clients found, using default client")
        return
    else:
        Var.MULTI_CLIENT = True
        print("Multi-Client Mode Enabled")
    
    async def start_client(client_id, token):
        try:
            # if len(token) >= 100:
            #     session_string=token
            #     bot_token=None
            #     print(f'Starting Client - {client_id} Using Session String')
            # else:
            #     session_string=None
            #     bot_token=token
            #     print(f'Starting Client - {client_id} Using Bot Token')
            if client_id == len(all_tokens):
                await asyncio.sleep(2)
                print("This will take some time, please wait...")
            client = TLClient(
                session=MemorySession(),
                api_id=Var.API_ID,
                api_hash=Var.API_HASH,
                flood_sleep_threshold=Var.SLEEP_THRESHOLD,
                receive_updates=False
            )
            await client.start(bot_token=token)   
            await client.startup()         
            client.id = (await client.get_me()).id
            work_loads[client_id] = 0
            return client_id, client
        except Exception:
            logging.error(f"Failed starting Client - {client_id} Error:", exc_info=True)
    
    clients = await asyncio.gather(*[start_client(i, token) for i, token in all_tokens.items()])
    multi_clients.update(dict(clients))