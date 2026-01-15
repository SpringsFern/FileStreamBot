> ⚠️ **NOTICE**  
> This repository has been **rewritten from scratch** and is now maintained at a new location:  
> 👉 [https://github.com/SpringsFern/tg-filestream](https://github.com/SpringsFern/tg-filestream)

# Telegram File Stream Bot
This bot will give you stream links for Telegram files without waiting for them to download.

### Original Repository
[TG-FileStreamBot](https://github.com/DeekshithSH/TG-FileStreamBot) is a modified version of [TG-FileStreamBot](https://github.com/EverythingSuckz/TG-FileStreamBot) by [EverythingSuckz](https://github.com/EverythingSuckz)

The main logic was taken from [Tulir Asokan](https://github.com/tulir)'s [tg filestream](https://github.com/tulir/TGFileStream) project.

## How to make your own
[Click here installation page](/docs/INSTALL.md)

## Environment Variables
### 🔒 Mandatory

- `API_ID` : Goto [my.telegram.org](https://my.telegram.org) to obtain this.
- `API_HASH` : Goto [my.telegram.org](https://my.telegram.org) to obtain this.
- `BOT_TOKEN` : Get the bot token from [@BotFather](https://telegram.dog/BotFather)
- `BIN_CHANNEL` : Create a new channel (private/public), post something in your channel. Forward that post to [@missrose_bot](https://telegram.dog/MissRose_bot) and **reply** `/id`. Now copy paste the forwarded channel ID in this field. 

### 🧩 Optional

- `ALLOWED_USERS`:  A list of user IDs separated by comma (,). If this is set, only the users in this list will be able to use the bot.
    > **Note**
    > Leave this field empty and anyone will be able to use your bot instance.
- `BLOCKED_USERS`:  A list of user IDs separated by commas (,). If this is set, the users in this list will be prevented from using the bot.
    > **Note**
    > User IDs in this field take precedence. Even if a user is in ALLOWED_USERS, they will be blocked if they are listed here
- `CACHE_SIZE` (default: 128) — Maximum number of file info entries cached per client. Each client (including those using MULTI_TOKEN) gets its own separate cache of this size
- `CHUNK_SIZE`: Size of the chunk to request from Telegram server when streaming a file [See more](https://core.telegram.org/api/files#downloading-files)
- `CONNECTION_LIMIT`:  (default 20) - The maximum number of connections to a single Telegram datacenter.
- `FQDN` :  A Fully Qualified Domain Name if present. Defaults to `WEB_SERVER_BIND_ADDRESS`
- `HAS_SSL` : (can be either `True` or `False`) If you want the generated links in https format.
- `HASH_LENGTH`: This is the custom hash length for generated URLs. The hash length must be greater than 5 and less than 64.
- `KEEP_ALIVE` : If you want to make the server ping itself every
- `NO_PORT` : (can be either `True` or `False`) If you don't want your port to be displayed. You should point your `PORT` to `80` (http) or `443` (https) for the links to work. Ignore this if you're on Heroku.
- `NO_UPDATE` if set to `true` bot won't respond to any messages
- `PING_INTERVAL` : The time in seconds you want the servers to be pinged each time to avoid sleeping (Only for Heroku). Defaults to `600` or 10 minutes.
- `PORT` : The port that you want your webapp to be listened to. Defaults to `8080`
- `REQUEST_LIMIT`: (default 5) - The maximum number of requests a single IP can have active at a time
- `SLEEP_THRESHOLD` : Set a sleep threshold for flood wait exceptions happening globally in this telegram bot instance, below which any request that raises a flood wait will be automatically invoked again after sleeping for the required amount of time. Flood wait exceptions requiring higher waiting times will be raised. Defaults to 60 seconds.
- `TRUST_HEADERS`: (defaults to true) - Whether or not to trust X-Forwarded-For headers when logging requests.
- `WEB_SERVER_BIND_ADDRESS` : Your server bind address. Defauls to `0.0.0.0`

### 🤖 Multi-Client Tokens

To enable multi-client, generate new bot tokens and add it as your environmental variables with the following key names. 

`MULTI_TOKEN1`: Add your first bot token here.

`MULTI_TOKEN2`: Add your second bot token here.

you may also add as many as bots you want. (max limit is not tested yet)
`MULTI_TOKEN3`, `MULTI_TOKEN4`, etc.

> **Warning**
> Don't forget to add all these bots to the `BIN_CHANNEL` for the proper functioning

## How to use the bot

:warning: Make sure all bots are added to the `BIN_CHANNEL` as **admins**.

- `/start` — Check if the bot is alive  
- Forward any media to get an instant stream link.

## FAQ

**Q: Do the stream links expire?**  
A: They are valid as long as your bot is alive and the log channel isn’t deleted.

## Contributing

Feel free to open issues or PRs with improvements or suggestions.

## Contact

Join the [Telegram Group](https://xn--r1a.click/AWeirdString) or [Channel](https://xn--r1a.click/SpringsFern) for updates.

## Credits

- [Me](https://github.com/DeekshithSH)
- [Lonami](https://github.com/Lonami) for his [Telethon Library](https://github.com/LonamiWebs/Telethon)
- [Tulir Asokan](https://github.com/tulir) for his [tg filestream](bit.ly/tg-stream)
- [EverythingSuckz](https://github.com/EverythingSuckz) for his [TG-FileStreamBot](https://github.com/EverythingSuckz/TG-FileStreamBot)
- [BlackStone](https://github.com/eyMarv) for adding multi-client support.
- [eyaadh](https://github.com/eyaadh) for his awesome [Megatron Bot](https://github.com/eyaadh/megadlbot_oss).
