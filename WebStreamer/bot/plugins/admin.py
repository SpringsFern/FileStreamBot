# This file is a part of FileStreamBot

# import os
# import time
# import string
# import random
# import asyncio
# import aiofiles
# import datetime
# from WebStreamer.utils.broadcast_helper import send_msg
from WebStreamer.utils.database import Database
from WebStreamer.bot import StreamBot
from WebStreamer.utils.file_properties import get_media_from_message
from WebStreamer.vars import Var
from telethon.types import User
from telethon.events import filters, NewMessage
db = Database(Var.DATABASE_URL, Var.SESSION_NAME)
broadcast_ids = {}

print("Hi")
@StreamBot.on(NewMessage, filters.Command("status") & filters.ChatType(User) & filters.Chats([Var.OWNER_ID]))
async def sts(event: NewMessage):
    await event.reply(text=f"""**Total Users in DB:** `{await db.total_users_count()}`
**Banned Users in DB:** `{await db.total_banned_users_count()}`
**Total Links Generated: ** `{await db.total_files()}`"""
    , markdown=True)

@StreamBot.on(NewMessage, filters.Command("ban") & filters.ChatType(User) & filters.Chats([Var.OWNER_ID]))
async def sts(event: NewMessage):
    usr_cmd = event.text.split()
    if len(usr_cmd) < 2:
        return await event.reply("Invalid Format\n/ban UserID\n`/ban UserID1 UserID2` .....")
    text="Banned Users:\n"
    for id in usr_cmd[1:]:
        if not await db.is_user_banned(int(id)):
            try:
                await db.ban_user(int(id))
                text+=f"`{id}`: Banned\n"
                #ToDo
                # await event.client.send_message(
                #     chat=event.client.resolve_peers(id),
                #     text="**Your Banned to Use This Bot**",
                #     markdown=True,
                #     link_preview=True
                # )
            except Exception as e:
                text+=f"`{id}`: Error `{e}`\n"
        else:
            text+=f"`{id}`: Already Banned\n"
    await event.reply(text)

@StreamBot.on(NewMessage, filters.Command("unban") & filters.ChatType(User) & filters.Chats([Var.OWNER_ID]))
async def sts(event: NewMessage):
    usr_cmd = event.text.split()
    if len(usr_cmd) < 2:
        return await event.reply("Invalid Format\n/unban UserID\n`/unban UserID1 UserID2` .....")
    text="Unbanned Users:\n"
    for id in usr_cmd[1:]:
        if await db.is_user_banned(int(id)):
            try:
                await db.unban_user(int(id))
                text+=f"`{id}`: Unbanned\n"
                #ToDo
                # await b.send_message(
                #     chat_id=id,
                #     text="**Your Unbanned now Use can use This Bot**",
                #     parse_mode=ParseMode.MARKDOWN,
                #     disable_web_page_preview=True
                # )
            except Exception as e:
                text+=f"`{id}`: Error `{e}`\n"
        else:
            text+=f"`{id}`: Not Banned\n"
    await event.reply(text)

#ToDo
# @StreamBot.on(NewMessage, filters.Command("broadcast") & filters.ChatType(User) & filters.Chats([Var.OWNER_ID]) & filters.reply)
# async def broadcast_(event: NewMessage):
#     all_users = await db.get_all_users()
#     broadcast_msg = m.reply_to_message
#     while True:
#         broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
#         if not broadcast_ids.get(broadcast_id):
#             break
#     out = await m.reply_text(
#         text=f"Broadcast initiated! You will be notified with log file when all the users are notified."
#     )
#     start_time = time.time()
#     total_users = await db.total_users_count()
#     done = 0
#     failed = 0
#     success = 0
#     broadcast_ids[broadcast_id] = dict(
#         total=total_users,
#         current=done,
#         failed=failed,
#         success=success
#     )
#     async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
#         async for user in all_users:
#             sts, msg = await send_msg(
#                 user_id=int(user['id']),
#                 message=broadcast_msg
#             )
#             if msg is not None:
#                 await broadcast_log_file.write(msg)
#             if sts == 200:
#                 success += 1
#             else:
#                 failed += 1
#             if sts == 400:
#                 await db.delete_user(user['id'])
#             done += 1
#             if broadcast_ids.get(broadcast_id) is None:
#                 break
#             else:
#                 broadcast_ids[broadcast_id].update(
#                     dict(
#                         current=done,
#                         failed=failed,
#                         success=success
#                     )
#                 )
#                 try:
#                     await out.edit_text(f"Broadcast Status\n\ncurrent: {done}\nfailed:{failed}\nsuccess: {success}")
#                 except:
#                     pass
#     if broadcast_ids.get(broadcast_id):
#         broadcast_ids.pop(broadcast_id)
#     completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
#     await asyncio.sleep(3)
#     await out.delete()
#     if failed == 0:
#         await m.reply_text(
#             text=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
#             quote=True
#         )
#     else:
#         await m.reply_document(
#             document='broadcast.txt',
#             caption=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
#             quote=True
#         )
#     os.remove('broadcast.txt')

@StreamBot.on(NewMessage, filters.Command("who") & filters.ChatType(User) & filters.Chats([Var.OWNER_ID]) & filters.Reply)
async def sts(event: NewMessage):
    media=get_media_from_message(await event.get_replied_message())
    if media:
        text="User List Who sent the file"
        file_info = await db.get_file_by_fileuniqueid(0, media.file_unique_id, True)
        async for x in file_info:
            text+=f"\n<a href='tg://user?id={x['user_id']}'>{x['user_id']}</a>"
        await event.reply(text)
    else:
        await event.reply("Please Reply to a File")