import html
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from .. import config, help_dict, log_errors, public_log_errors

# Mute Permissions
mute_permission = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_stickers=False,
    can_send_animations=False,
    can_send_games=False,
    can_use_inline_bots=False,
    can_add_web_page_previews=False,
    can_send_polls=False,
    can_change_info=False,
    can_invite_users=False,
    can_pin_messages=False,
)
# Unmute permissions
unmute_permissions = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_stickers=True,
    can_send_animations=True,
    can_send_games=True,
    can_use_inline_bots=True,
    can_add_web_page_previews=True,
    can_send_polls=True,
    can_change_info=False,
    can_invite_users=True,
    can_pin_messages=False,
)

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['promote'], prefixes=config['config']['prefixes']))
@log_errors
async def promote(client, message):
	pass

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['demote'], prefixes=config['config']['prefixes']))
@log_errors
async def demote(client, message):
	pass

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['m', 'mute'], prefixes=config['config']['prefixes']))
@log_errors
async def mute(client, message):
	pass

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['um', 'unmute'], prefixes=config['config']['prefixes']))
@log_errors
async def unmute(client, message):
	pass

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['b', 'ban'], prefixes=config['config']['prefixes']))
@log_errors
async def banhammer(client, message):
	pass

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['ub', 'unban'], prefixes=config['config']['prefixes']))
@log_errors
async def unbanhammer(client, message):
	pass

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['k', 'kick'], prefixes=config['config']['prefixes']))
@log_errors
async def kick(client, message):
	pass

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['testtest'], prefixes=config['config']['prefixes']))
@log_errors
@public_log_errors
async def delete(client, message):
    messages = set((message.message_id,))
    reply = message.reply_to_message
    if not getattr(reply, 'empty', True):
        messages.add(reply.message_id)
    else:
        async for i in client.iter_history(message.chat.id, offset=1):
            if i.outgoing:
                messages.add(i.message_id)
                break
    await client.delete_messages(message.chat.id, messages)

help_dict['delete'] = ('Moderation',
'''{prefix}delete <i>(maybe reply to a message)</i> - Deletes the replied to message, or your latest message
Aliases: {prefix}d, {prefix}del

{prefix}selfyeetpurge <i>(as reply to a message)</i> - {prefix}yp but only your messages
Aliases: {prefix}syp''')
