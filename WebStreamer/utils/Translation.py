# This file is a part of FileStreamBot

from telethon import Button
from WebStreamer.vars import Var

class Language:
    def __new__(self, message=None):
        # if getattr(message.from_user, 'language_code', 'Unknown') in self.available:
        #     return getattr(self, getattr(message.from_user, 'language_code', "en"), self.en)
        # else:
        return self.en

    available=['en', 'language_code']

    class en:
        START_TEXT: str = """
👋 Hi there, <a href="tg://user?id={}">{}</a>!

I am the File Stream Bot, your go-to assistant for generating external download links from any file or media you send. 
Feel free to explore my features and see how I can make file sharing a breeze.

Here's what you can do:
- Send me any file or media, and I'll provide you with an external download link.
- Need help or have a question? Just click on the 'Help' button below for more information.
"""

        HELP_TEXT: str = """
- Send any file or media to me.
- I will provide an external download link.
- For support or to report a bug <b><a href='https://t.me/{}'>[ click here] </a></b>.
"""

        ABOUT_TEXT: str = """
<b>Bot Name:</b> TG-FileStreamBot
<b>Version:</b> {}
<b>Last Updated:</b> 20-July-2023
"""

        STREAM_MSG_TEXT: str = """
<u><i>Your Link is Generated!</i></u>\n
<b>📂 File Name:</b> <i>{name}</i>\n
<b>📦 File Size:</b> <i>{size}</i>\n
<b>📥 Download:</b> <i>{link}</i>\n
Link generated using <a href='https://t.me/{username}'>{firstname}</a>.\n
<b>Note:</b> Link will only work for 24 hours.
"""

#----------------------#
# Change the Text's below to add suport for your language

# you can find the language_code for your language here
# https://en.wikipedia.org/wiki/IETF_language_tag#List_of_common_primary_language_subtags
# change language_code with your language code
# eg:    class kn(object):
    class language_code:
        START_TEXT: str = "Hi <a href=tg://user?id={}>{}</a>"

        HELP_TEXT: str = "Help Text"

        ABOUT_TEXT: str = "<b>🔸Vᴇʀꜱɪᴏɴ : {}</b>"

        STREAM_MSG_TEXT: str = """
<u><i>Your Link is Generated!</i></u>
<b>📂 File Name:</b> <i>{name}</i>
<b>📦 File Size:</b> <i>{size}</i>
<b>📥 Download:</b> <i>{link}</i>
Link generated using <a href='https://t.me/{username}'>{firstname}</a>.
<b>Note:</b> Link will only work for 24 hours."""

# ------------------------------------------------------------------------------


class BUTTON(object):
    START_BUTTONS = [
        [
            Button.inline('Hᴇʟᴘ', 'help'),
            Button.inline('Aʙᴏᴜᴛ', 'about'),
            Button.inline('Cʟᴏsᴇ', 'close')
        ],
        [Button.url("📢 Bot Channel", f'https://t.me/{Var.UPDATES_CHANNEL}')]
    ]
    HELP_BUTTONS = [
        [
            Button.inline('Hᴏᴍᴇ', 'home'),
            Button.inline('Aʙᴏᴜᴛ', 'about'),
            Button.inline('Cʟᴏsᴇ', 'close'),
        ],
        [Button.url("📢 Bot Channel", f'https://t.me/{Var.UPDATES_CHANNEL}')]
    ]
    ABOUT_BUTTONS = [
        [
            Button.inline('Hᴏᴍᴇ', 'home'),
            Button.inline('Hᴇʟᴘ', 'help'),
            Button.inline('Cʟᴏsᴇ', 'close'),
        ],
        [Button.url("📢 Bot Channel", f'https://t.me/{Var.UPDATES_CHANNEL}')]
    ]
