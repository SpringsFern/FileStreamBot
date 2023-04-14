# This file is a part of FileStreamBot


import asyncio
from WebStreamer.utils.Translation import Language
from WebStreamer.bot import StreamBot
from WebStreamer.utils.database import Database
from WebStreamer.utils.file_properties import gen_link, get_file_info, get_hash
from WebStreamer.vars import Var
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
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
async def private_receive_handler(c: Client, m: Message):
    lang = Language(m)
    # Check The User is Banned or Not
    if await db.is_user_banned(m.from_user.id):
        await c.send_message(
                chat_id=m.chat.id,
                text=lang.ban_text.format(Var.OWNER_ID),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        return
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"Nᴇᴡ Usᴇʀ Jᴏɪɴᴇᴅ : \n\nNᴀᴍᴇ : [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Sᴛᴀʀᴛᴇᴅ Yᴏᴜʀ Bᴏᴛ !!"
        )
    if Var.FORCE_UPDATES_CHANNEL:
        try:
            user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
            if user.status == "kicked":
                await c.send_message(
                    chat_id=m.chat.id,
                    text=lang.ban_text.format(Var.OWNER_ID),
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await c.send_message(
                chat_id=m.chat.id,
                text="""<i>Jᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜꜱᴇ ᴍᴇ 🔐</i>""",
                reply_markup=InlineKeyboardMarkup(
                    [[ InlineKeyboardButton("Jᴏɪɴ ɴᴏᴡ 🔓", url=f"https://t.me/{Var.UPDATES_CHANNEL}") ]]
                ),
                parse_mode=ParseMode.HTML
            )
            return
        except Exception:
            await c.send_message(
                chat_id=m.chat.id,
                text=f"**Sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ Wʀᴏɴɢ. [Cᴏɴᴛᴀᴄᴛ ᴍʏ ʙᴏss](tg://user?id={Var.OWNER_ID})**",
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True)
            return

    try:
        inserted_id=await db.add_file(get_file_info(m))
        reply_markup, Stream_Text, stream_link = await gen_link(m=m, from_channel=False, _id=inserted_id)
        await m.reply_text(
            text=Stream_Text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            quote=True
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.value)}s")
        await asyncio.sleep(e.value)
        await c.send_message(chat_id=Var.BIN_CHANNEL, text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.value)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**𝚄𝚜𝚎𝚛 𝙸𝙳 :** `{str(m.from_user.id)}`", disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)

@StreamBot.on_message(filters.channel & (filters.document | filters.video), group=-1)
async def channel_receive_handler(bot, broadcast: Message):
    if int(broadcast.chat.id) in Var.BANNED_CHANNELS:
        await bot.leave_chat(broadcast.chat.id)
        return
    try:
        log_msg = await broadcast.copy(chat_id=Var.BIN_CHANNEL)
        stream_link = "{}dl/{}{}".format(Var.URL, get_hash(log_msg), log_msg.id)
        await log_msg.reply_text(
            text=f"**Cʜᴀɴɴᴇʟ Nᴀᴍᴇ:** `{broadcast.chat.title}`\n**Cʜᴀɴɴᴇʟ ID:** `{broadcast.chat.id}`\n**Rᴇǫᴜᴇsᴛ ᴜʀʟ:** https://t.me/{(await bot.get_me()).username}?start=msgid_{str(log_msg.id)}",
            # text=f"**Cʜᴀɴɴᴇʟ Nᴀᴍᴇ:** `{broadcast.chat.title}`\n**Cʜᴀɴɴᴇʟ ID:** `{broadcast.chat.id}`\n**Rᴇǫᴜᴇsᴛ ᴜʀʟ:** https://t.me/FxStreamBot?start=msgid_{str(log_msg.id)}",
            quote=True,
            parse_mode=ParseMode.MARKDOWN
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.id,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Dᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ 📥", url=stream_link)]])
                # [[InlineKeyboardButton("Dᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ 📥", url=f"https://t.me/{(await bot.get_me()).username}?start=msgid_{str(log_msg.id)}")]])
            # [[InlineKeyboardButton("Dᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ 📥", url=f"https://t.me/FxStreamBot?start=msgid_{str(log_msg.id)}")]])
        )
    except FloodWait as w:
        print(f"Sleeping for {str(w.value)}s")
        await asyncio.sleep(w.value)
        await bot.send_message(chat_id=Var.BIN_CHANNEL,
                             text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(w.value)}s from {broadcast.chat.title}\n\n**Cʜᴀɴɴᴇʟ ID:** `{str(broadcast.chat.id)}`",
                             disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await bot.send_message(chat_id=Var.BIN_CHANNEL, text=f"**#ᴇʀʀᴏʀ_ᴛʀᴀᴄᴇʙᴀᴄᴋ:** `{e}`", disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
        print(f"Cᴀɴ'ᴛ Eᴅɪᴛ Bʀᴏᴀᴅᴄᴀsᴛ Mᴇssᴀɢᴇ!\nEʀʀᴏʀ: {e}")
