from pyrogram.errors import UserNotParticipant
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from WebStreamer.utils.Translation import Language
from WebStreamer.utils.database import Database
from WebStreamer.utils.file_properties import get_media_file_size, get_name
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.vars import Var

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)

async def is_user_joined(bot, message:Message,lang):
    try:
        user = await bot.get_chat_member(Var.UPDATES_CHANNEL, message.chat.id)
        if user.status == "BANNED":
            await message.reply_text(
                text=lang.ban_text.format(Var.OWNER_ID),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return False
    except UserNotParticipant:
        await message.reply_text(
            text="<i>Jᴏɪɴ ᴍʏ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴍᴇ 🔐</i>",
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton("Jᴏɪɴ ɴᴏᴡ 🔓", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                    ]]
            ),
            parse_mode=ParseMode.HTML
        )
        return False
    except Exception:
        await message.reply_text(
            text=f"<i>Sᴏᴍᴇᴛʜɪɴɢ ᴡʀᴏɴɢ ᴄᴏɴᴛᴀᴄᴛ ᴍʏ ᴅᴇᴠᴇʟᴏᴘᴇʀ</i> <b><a href='https://t.me/{Var.UPDATES_CHANNEL}'>[ ᴄʟɪᴄᴋ ʜᴇʀᴇ ]</a></b>",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True)
        return False
    return True

# Generate Text, Stream Link, reply_markup
async def gen_link(m: Message, from_channel: bool, _id):
    """Generate Text for Stream Link, Reply Text and reply_markup"""
    # lang = getattr(Language, message.from_user.language_code)
    lang = Language(m)
    file_name = get_name(m)
    file_size = humanbytes(get_media_file_size(m))
    page_link = f"{Var.URL}watch/{_id}"
    
    stream_link = f"{Var.URL}dl/{_id}"
    Stream_Text=lang.stream_msg_text.format(file_name, file_size, stream_link, page_link)
    reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🖥STREAM", url=page_link), InlineKeyboardButton("Dᴏᴡɴʟᴏᴀᴅ 📥", url=stream_link)]
            ]
        )

    return reply_markup, Stream_Text

async def is_user_banned(message, lang):
    if await db.is_user_banned(message.from_user.id):
        await message.reply_text(
            text=lang.ban_text.format(Var.OWNER_ID),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return True
    return False

async def is_user_exist(bot, message):
    if not bool(await db.get_user(message.from_user.id)):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"**Nᴇᴡ Usᴇʀ Jᴏɪɴᴇᴅ:** \n\n__Mʏ Nᴇᴡ Fʀɪᴇɴᴅ__ [{message.from_user.first_name}](tg://user?id={message.from_user.id}) __Sᴛᴀʀᴛᴇᴅ Yᴏᴜʀ Bᴏᴛ !!__"
        )

async def is_user_accepted_tos(message: Message):
    user=await db.get_user(message.from_user.id)
    if not ("agreed_to_tos" in user) or not (user["agreed_to_tos"]):
        await message.reply(f"Hi {message.from_user.mention},\nplease read and accept the Terms of Service to continue using the bot")
        await message.reply_text(
            Var.TOS,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("I accept the TOS", callback_data=f"accepttos_{message.from_user.id}")]])
            )
        return False
    return True