import html, asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from .. import config, help_dict, get_entity, log_chat, log_errors, CheckAdmin

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

	if message.chat.type in ["group", "supergroup"]:
		await message.edit("<code>How am I supposed to kick in a damn private chat?</code>")
		await asyncio.sleep(3)
		await message.delete()
		return

	if await CheckAdmin(message):
		entity = message.chat
		command = message.command
		command.pop(0)
		chat_id = message.chat.id
		entity_id = command
		reason = ""

		if len(command) >= 2:
			# -1001450488581 @rDakotaBot lel some optional reason
			try:
				noob = int(command[0])
				if noob > 0:
					entity_id = noob
				else:
					chat_id = noob
			except ValueError:
				# assume it's a channel name.
				chat_id = noob
			
			# now for arg 2
			try:
				noob = int(command[1])
				if noob > 0:
					entity_id = noob
				else:
					chat_id = noob
			except ValueError:
				# assume it's an entity name.
				entity_id = noob

			if len(command) > 2:
				reason = " ".join(command[2:])

		elif len(command) == 1:
			entity_id = command[0]
		elif not getattr(message.reply_to_message, 'empty', True):
			entity_id = message.reply_to_message.from_user.id
			chat_id = message.reply_to_message.chat.id
		else:
			# what the fuck
			pass

		# Attempt to resolve
		entity_id, entity_client = await get_entity(client, entity_id)
		chat_id, chat_client = await get_entity(client, chat_id)

		await client.kick_chat_member(
			chat_id=chat_id.id,
			user_id=entity_id.id
		)

		# delete our kick command so pajeets don't try and run it themselves
		await message.delete()

		# log if we successfully kicked someone.
		chat_name = html.escape(chat_id.title)
		if message.chat.username:
			chat_name = f'<a href="https://t.me/{chat_id.username}">{chat_name}</a>'

		chat_text = '<b>Kick Event</b>\n- <b>Chat:</b> ' + chat_name + '\n- <b>Kicked:</b> '
		user_text = entity_id.first_name
		if entity_id.last_name:
			user_text += f' {entity_id.last_name} <code>[{entity.id}]</code>'
		user_text = html.escape(user_text or 'Empty???')
		if entity_id.is_verified:
			user_text += ' <code>[VERIFIED]</code>'
		if entity_id.is_support:
			user_text += ' <code>[SUPPORT]</code>'
		if entity_id.is_scam:
			user_text += ' <code>[SCAM]</code>'
			user_text += f' [<code>{entity_id.id}</code>]'
		chat_text += f'{user_text}\n- <b>Reason:</b> {html.escape(reason.strip()[:1000])}'

		await log_chat(chat_text)

help_dict['moderation'] = ('Moderation',
'''{prefix}kick <i>[channel id|user id] [user id]</i> - Deletes the replied to message, or user's location based on optional channel id and user id
Aliases: {prefix}k
''')
