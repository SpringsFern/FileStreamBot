# This file is a part of FileStreamBot

import random
from urllib.parse import quote_plus
from WebStreamer.bot import StreamBot
from WebStreamer.utils.file_properties import gen_link, get_media_file_unique_id
from WebStreamer.vars import Var
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.utils.database import Database
from pyrogram import filters, Client
import WebStreamer.utils.Translation as Translation
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import UserNotParticipant, MessageDeleteForbidden

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)

START_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Hᴇʟᴘ', callback_data='help'),
        InlineKeyboardButton('Aʙᴏᴜᴛ', callback_data='about'),
        InlineKeyboardButton('Cʟᴏsᴇ', callback_data='close')
        ],
        [InlineKeyboardButton("📢 Bot Channel", url=f'https://t.me/{Var.UPDATES_CHANNEL}')]
        ]
    )
HELP_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Hᴏᴍᴇ', callback_data='home'),
        InlineKeyboardButton('Aʙᴏᴜᴛ', callback_data='about'),
        InlineKeyboardButton('Cʟᴏsᴇ', callback_data='close'),
        ],
        [InlineKeyboardButton("📢 Bot Channel", url=f'https://t.me/{Var.UPDATES_CHANNEL}')]
        ]
    )
ABOUT_BUTTONS = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Hᴏᴍᴇ', callback_data='home'),
        InlineKeyboardButton('Hᴇʟᴘ', callback_data='help'),
        InlineKeyboardButton('Cʟᴏsᴇ', callback_data='close'),
        ],
        [InlineKeyboardButton("📢 Bot Channel", url=f'https://t.me/{Var.UPDATES_CHANNEL}')]
        ]
    )
deldbtnmsg=["Your Already Deleted the Link", "You can't undo the Action", "You can Resend the File to Regenerate New Link", "Why Clicking me Your Link is Dead", "This is Just a Button Showing that Your Link is Deleted"]

@StreamBot.on_callback_query()
async def cb_data(bot, update: CallbackQuery):
    # lang = getattr(Translation, update.from_user.language_code)
    lang = getattr(Translation, "en")
    if update.data == "home":
        await update.message.edit_text(
            text=lang.START_TEXT.format(update.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=START_BUTTONS
        )
    elif update.data == "help":
        await update.message.edit_text(
            text=lang.HELP_TEXT,
            disable_web_page_preview=True,
            reply_markup=HELP_BUTTONS
        )
    elif update.data == "about":
        await update.message.edit_text(
            text=lang.ABOUT_TEXT,
            disable_web_page_preview=True,
            reply_markup=ABOUT_BUTTONS
        )
    elif update.data == "close":
        await update.message.delete()
    elif update.data == "msgdeleted":
        await update.answer(random.choice(deldbtnmsg), show_alert=True)
    else:
        usr_cmd = update.data.split("_")
        if usr_cmd[0] == "msgdelconf2":
            await update.message.edit_text(
            text=update.message.text,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✔️", callback_data=f"msgdelyes_{usr_cmd[1]}_{usr_cmd[2]}"), InlineKeyboardButton("✖️", callback_data=f"msgdelno_{usr_cmd[1]}_{usr_cmd[2]}")]])
        )
        elif usr_cmd[0] == "msgdelno":
            get_msg = await bot.get_messages(chat_id=Var.BIN_CHANNEL, message_ids=int(usr_cmd[1]))
            if get_media_file_unique_id(get_msg) == usr_cmd[2]:
                reply_markup, Stream_Text, stream_link = await gen_link(m=update, log_msg=get_msg, from_channel=False)

                await update.message.edit_text(
                text=Stream_Text,
                disable_web_page_preview=True,
                reply_markup=reply_markup
                )
            elif resp.empty:
                await update.answer("Sorry Your File is Missing from the Server", show_alert=True)
            else:
                await update.answer("Message id and file_unique_id miss match", show_alert=True)
        elif usr_cmd[0] == "msgdelyes":
            try:
                resp = await bot.get_messages(Var.BIN_CHANNEL, int(usr_cmd[1]))
                if get_media_file_unique_id(resp) == usr_cmd[2]:
                    await bot.delete_messages(
                        chat_id=Var.BIN_CHANNEL,
                        message_ids=int(usr_cmd[1])
                    )
                    await update.message.edit_text(
                    text=update.message.text,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Link Deleted", callback_data="msgdeleted")]])
                    )
                elif resp.empty:
                    await update.answer("Sorry Your File is Missing from the Server", show_alert=True)
                else:
                    await update.answer("Message id and file_unique_id miss match", show_alert=True)
            except MessageDeleteForbidden as e:
                print(e)
                await bot.send_message(
                    chat_id=Var.BIN_CHANNEL,
                    text=f"**#ᴇʀʀᴏʀ_ᴛʀᴀᴄᴇʙᴀᴄᴋ:** `{e}`\n#Delete_Link", disable_web_page_preview=True, parse_mode="Markdown",
                )
                await update.answer(text='message too old', show_alert=True)
            except Exception as e:
                print(e)
                error_id=await bot.send_message(
                    chat_id=Var.BIN_CHANNEL,
                    text=f"**#ᴇʀʀᴏʀ_ᴛʀᴀᴄᴇʙᴀᴄᴋ:** `{e}`\n#Delete_Link", disable_web_page_preview=True, parse_mode="Markdown",
                )
                await update.message.reply_text(
                    text=f"**#ᴇʀʀᴏʀ_ᴛʀᴀᴄᴇʙᴀᴄᴋ:** `message-id={error_id.message_id}`\nYou can get Help from [Public Link Generator (Support)](https://t.me/PublicLinkGenerator)", disable_web_page_preview=True, parse_mode="Markdown",
                )
        else:
            await update.message.delete()

@StreamBot.on_message(filters.command('start') & filters.private & ~filters.edited)
async def start(b, m):
    # lang = getattr(Translation, m.from_user.language_code)
    lang = getattr(Translation, "en")
    # Check The User is Banned or Not
    if await db.is_user_banned(m.from_user.id):
        await b.send_message(
                chat_id=m.chat.id,
                text=lang.ban_text.format(Var.OWNER_ID),
                parse_mode="markdown",
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
                    parse_mode="markdown",
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
                parse_mode="HTML"
            )
            return
        except Exception:
            await b.send_message(
                chat_id=m.chat.id,
                text="<i>Sᴏᴍᴇᴛʜɪɴɢ ᴡʀᴏɴɢ ᴄᴏɴᴛᴀᴄᴛ ᴍʏ ᴅᴇᴠᴇʟᴏᴘᴇʀ</i> <b><a href='https://t.me/PublicLinkGenerator'>[ ᴄʟɪᴄᴋ ʜᴇʀᴇ ]</a></b>",
                parse_mode="HTML",
                disable_web_page_preview=True)
            return
    await m.reply_text(
        text=lang.START_TEXT.format(m.from_user.mention),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=START_BUTTONS
        )


@StreamBot.on_message(filters.private & filters.command(["about"]))
async def start(bot, update):
    # lang = getattr(Translation, update.from_user.language_code)
    lang = getattr(Translation, "en")
    await update.reply_text(
        text=lang.ABOUT_TEXT.format(update.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=ABOUT_BUTTONS
    )


@StreamBot.on_message((filters.command('help')) & filters.private & ~filters.edited)
async def help_handler(bot, message):
    # lang = getattr(Translation, message.from_user.language_code)
    lang = getattr(Translation, "en")
    # Check The User is Banned or Not
    if await db.is_user_banned(message.from_user.id):
        await bot.send_message(
                chat_id=message.chat.id,
                text=lang.ban_text.format(Var.OWNER_ID),
                parse_mode="markdown",
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
                    parse_mode="HTML",
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
                parse_mode="markdown"
            )
            return
        except Exception:
            await bot.send_message(
                chat_id=message.chat.id,
                text="__Sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ Wʀᴏɴɢ. Cᴏɴᴛᴀᴄᴛ ᴍᴇ__ [ ᴄʟɪᴄᴋ ʜᴇʀᴇ ](https://t.me/PublicLinkGenerator).",
                parse_mode="markdown",
                disable_web_page_preview=True)
            return
    await message.reply_text(
        text=lang.HELP_TEXT,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=HELP_BUTTONS
        )

# -----------------------------Only for me you can remove below line -------------------------------------------------------

@StreamBot.on_message(filters.command('getid') & filters.private & ~filters.edited)
async def start(b, m):
    await b.send_message(
        chat_id=m.chat.id,
        text=f"Your ID is: `{m.chat.id}`"
    )