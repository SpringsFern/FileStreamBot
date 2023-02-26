# This file is a part of FileStreamBot

from WebStreamer.bot import StreamBot
from WebStreamer.vars import Var
from WebStreamer.utils.database import Database
from pyrogram import filters, Client
from WebStreamer.utils.Translation import Language, BUTTON
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from pyrogram.enums.parse_mode import ParseMode

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)

@StreamBot.on_message(filters.command('start') & filters.private)
async def start(b, m):
    lang = Language(m)
    # Check The User is Banned or Not
    if await db.is_user_banned(m.from_user.id):
        await b.send_message(
                chat_id=m.chat.id,
                text=lang.ban_text.format(Var.OWNER_ID),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        return
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await b.send_message(
            Var.BIN_CHANNEL,
            f"**Nᴇᴡ Usᴇʀ Jᴏɪɴᴇᴅ:** \n\n__Mʏ Nᴇᴡ Fʀɪᴇɴᴅ__ [{m.from_user.first_name}](tg://user?id={m.from_user.id}) __Sᴛᴀʀᴛᴇᴅ Yᴏᴜʀ Bᴏᴛ !!__"
        )
    usr_cmd = m.text.split("_")[-1]
    if Var.FORCE_UPDATES_CHANNEL:
        try:
            user = await b.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
            if user.status == "kicked":
                await b.send_message(
                    chat_id=m.chat.id,
                    text=lang.ban_text.format(Var.OWNER_ID),
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await b.send_message(
                chat_id=m.chat.id,
                text="<i>Jᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ 🔐</i>",
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton("Jᴏɪɴ ɴᴏᴡ 🔓", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                        ]]
                ),
                parse_mode=ParseMode.HTML
            )
            return
        except Exception:
            await b.send_message(
                chat_id=m.chat.id,
                text=f"<i>Sᴏᴍᴇᴛʜɪɴɢ ᴡʀᴏɴɢ ᴄᴏɴᴛᴀᴄᴛ ᴍʏ ᴅᴇᴠᴇʟᴏᴘᴇʀ</i> <b><a href='https://t.me/{Var.UPDATES_CHANNEL}'>[ ᴄʟɪᴄᴋ ʜᴇʀᴇ ]</a></b>",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True)
            return
    await m.reply_text(
        text=lang.START_TEXT.format(m.from_user.mention),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=BUTTON.START_BUTTONS
        )


@StreamBot.on_message(filters.private & filters.command(["about"]))
async def start(bot, update):
    lang = Language(update)
    await update.reply_text(
        text=lang.ABOUT_TEXT.format(update.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=BUTTON.ABOUT_BUTTONS
    )


@StreamBot.on_message((filters.command('help')) & filters.private)
async def help_handler(bot, message):
    lang = Language(message)
    # Check The User is Banned or Not
    if await db.is_user_banned(message.from_user.id):
        await bot.send_message(
                chat_id=message.chat.id,
                text=lang.ban_text.format(Var.OWNER_ID),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        return
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"**Nᴇᴡ Usᴇʀ Jᴏɪɴᴇᴅ **\n\n__Mʏ Nᴇᴡ Fʀɪᴇɴᴅ__ [{message.from_user.first_name}](tg://user?id={message.from_user.id}) __Started Your Bot !!__"
        )
    if Var.FORCE_UPDATES_CHANNEL:
        try:
            user = await bot.get_chat_member(Var.UPDATES_CHANNEL, message.chat.id)
            if user.status == "kicked":
                await bot.send_message(
                    chat_id=message.chat.id,
                    text=lang.ban_text.format(Var.OWNER_ID),
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await bot.send_message(
                chat_id=message.chat.id,
                text="**Pʟᴇᴀsᴇ Jᴏɪɴ Mʏ Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs Bᴏᴛ!**\n\n__Dᴜᴇ ᴛᴏ Oᴠᴇʀʟᴏᴀᴅ, Oɴʟʏ Cʜᴀɴɴᴇʟ Sᴜʙsᴄʀɪʙᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜᴇ Bᴏᴛ!__",
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton("🤖 Jᴏɪɴ Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                        ]]
                ),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        except Exception:
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"__Sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ Wʀᴏɴɢ. Cᴏɴᴛᴀᴄᴛ ᴍᴇ__ [ ᴄʟɪᴄᴋ ʜᴇʀᴇ ](https://t.me/{Var.UPDATES_CHANNEL}).",
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True)
            return
    await message.reply_text(
        text=lang.HELP_TEXT.format(Var.UPDATES_CHANNEL),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=BUTTON.HELP_BUTTONS
        )

# -----------------------------Only for me you can remove below line -------------------------------------------------------

@StreamBot.on_message(filters.command('getid') & filters.private)
async def start(b, m):
    await b.send_message(
        chat_id=m.chat.id,
        text=f"Your ID is: `{m.chat.id}`"
    )