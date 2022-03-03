# (c)  @DeekshithSH

from WebStreamer.utils import Translation
from WebStreamer.vars import Var
from pyrogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from pyrogram import Client, filters
from WebStreamer.bot import StreamBot
from WebStreamer.utils.database import Database
db = Database(Var.DATABASE_URL, Var.SESSION_NAME)

SETTINGS_BTN=ReplyKeyboardMarkup(
        [
            ["🔗Link Type"],
            ["📚Help","⚙️Close","status📊"]
        ],
        resize_keyboard=True
    )
SETTINGS_LinkType_BTN=ReplyKeyboardMarkup(
        [
            ["🔗With Name","🔗Without Name"],
            ["🔗With Both", "🔗Current Type"]
        ],
        resize_keyboard=True
    )

@StreamBot.on_message(filters.private & filters.command("settings"))
async def start(b: Client, m: Message):
    # lang = getattr(Translation, m.from_user.language_code)
    lang = getattr(Translation, "en")
    if await db.is_user_banned(m.from_user.id):
        await b.send_message(
                chat_id=m.chat.id,
                text=lang.ban_text,
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
    user, in_db = await db.Current_Settings_Link(m.from_user.id)
    if not in_db:
        await db.setttings_default(m.from_user.id)
        await m.reply_text(text="Created Settings in DB")
    await m.reply_text(
        text=lang.SETTINGS_TEXT,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=SETTINGS_BTN
        )

@StreamBot.on_message(filters.private & filters.regex("⚙️Close") & ~filters.edited)
async def close_settings(b, m):
    # lang = getattr(Translation, m.from_user.language_code)
    lang = getattr(Translation, "en")
    await m.reply_text(
    text="Settings Closed",
    parse_mode="HTML",
    disable_web_page_preview=True,
    reply_markup=ReplyKeyboardRemove(True)
    )

@StreamBot.on_message(filters.private & filters.regex("🔗Link Type") & ~filters.edited)
async def close_settings(b, m):
    # lang = getattr(Translation, m.from_user.language_code)
    lang = getattr(Translation, "en")
    await m.reply_text(
    text="Select Link Type",
    parse_mode="HTML",
    disable_web_page_preview=True,
    reply_markup=SETTINGS_LinkType_BTN
    )
    await m.delete()

@StreamBot.on_message(filters.private & filters.regex("🔗With Name") & ~filters.edited)
async def close_settings(b, m: Message):
    try:
        # lang = getattr(Translation, m.from_user.language_code)
        lang = getattr(Translation, "en")
        user, in_db = await db.Current_Settings_Link(m.from_user.id)
        if not in_db:
            await m.reply_text(text="First Send /settings then use This Keyword")
            return
        await db.Settings_Link_WithName(m.from_user.id)
        user, in_db = await db.Current_Settings_Link(m.from_user.id)

        await m.reply_text(
        text=f"Generate Link with FileName",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardRemove(True)
        )
        await m.delete()
    except Exception as e:
        await m.reply_text(
        text=f"**#ᴇʀʀᴏʀ_ᴛʀᴀᴄᴇʙᴀᴄᴋ:** `{e}`\n#Settings",
        disable_web_page_preview=True,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(True)
        )

@StreamBot.on_message(filters.private & filters.regex("🔗Without Name") & ~filters.edited)
async def close_settings(b, m):
    try:
        # lang = getattr(Translation, m.from_user.language_code)
        lang = getattr(Translation, "en")
        user, in_db = await db.Current_Settings_Link(m.from_user.id)
        if not in_db:
            await m.reply_text(text="First Send /settings then use This Keyword")
            return
        await db.Settings_Link_WithoutName(m.from_user.id)
        user, in_db = await db.Current_Settings_Link(m.from_user.id)

        await m.reply_text(
        text=f"Generate Link without FileName",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardRemove(True)
        )
        await m.delete()
    except Exception as e:
        await m.reply_text(
        text=f"**#ᴇʀʀᴏʀ_ᴛʀᴀᴄᴇʙᴀᴄᴋ:** `{e}`\n#Settings",
        disable_web_page_preview=True,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(True)
        )

@StreamBot.on_message(filters.private & filters.regex("🔗Current Type") & ~filters.edited)
async def close_settings(b, m):
    try:
        # lang = getattr(Translation, m.from_user.language_code)
        lang = getattr(Translation, "en")
        settings, in_db = await db.Current_Settings_Link(m.from_user.id)
        if not in_db:
            await m.reply_text(text="First Send /settings then use This Keyword")
            return
        if in_db and settings['LinkWithBoth']:
            text="New Link will Generate with and without FileName\nYou will get Two Download Link\nNote: Telegram Don't Provide any FileName for Video, Photo"
        elif in_db and not settings['LinkWithName']:
            text="Generate Link without FileName"
        elif in_db and settings['LinkWithName']:
            text="Generate Link with FileName"
        else:
            text="Generate Link with FileName"
        await m.reply_text(
        text=text,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardRemove(True)
        )
        await m.delete()
    except Exception as e:
        await m.reply_text(
        text=f"**#ᴇʀʀᴏʀ_ᴛʀᴀᴄᴇʙᴀᴄᴋ:** `{e}`\n#Settings",
        disable_web_page_preview=True,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(True)
        )

@StreamBot.on_message(filters.private & filters.regex("🔗With Both") & ~filters.edited)
async def link_type(b, m):
    try:
        # lang = getattr(Translation, m.from_user.language_code)
        lang = getattr(Translation, "en")
        user, in_db = await db.Current_Settings_Link(m.from_user.id)
        if not in_db:
            await m.reply_text(text="First Send /settings then use This Keyword")
            return
        await db.Settings_Link_WithBoth(m.from_user.id)
        user, in_db = await db.Current_Settings_Link(m.from_user.id)
        await m.reply_text(
        text=f"New Link will Generate with and without FileName\nYou will get Two Download Link\nNote: Telegram Don't Provide any FileName for Video, Photo",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardRemove(True)
        )
        await m.delete()
    except Exception as e:
        await m.reply_text(
        text=f"**#ᴇʀʀᴏʀ_ᴛʀᴀᴄᴇʙᴀᴄᴋ:** `{e}`\n#Settings",
        disable_web_page_preview=True,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(True)
        )