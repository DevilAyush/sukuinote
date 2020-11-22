import html
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from .. import config, help_dict, log_errors, public_log_errors

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['block'], prefixes=config['config']['prefixes']))
@log_errors
async def block(client, message):
	pass

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['unblock'], prefixes=config['config']['prefixes']))
@log_errors
async def unblock(client, message):
	pass