import html, asyncio, time
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from .. import config, help_dict, get_entity, log_chat, log_errors, CheckAdmin, is_admin

# Mute Permissions
mute_permissions = ChatPermissions(
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

# Convenience functions
async def _CheckGroupAndPerms(message):
	if not message.chat.type in ["group", "supergroup"]:
		await message.edit("<code>How am I supposed to do this in a damn private chat?</code>")
		await asyncio.sleep(3)
		await message.delete()
		return False

	if not await CheckAdmin(message):
		await message.edit("<code>I am not an admin here lmao. What am I doing?</code>")
		await asyncio.sleep(3)
		await message.delete()
		return False

	return True


async def _ParseCommandArguments(client, message):
	""" Parse command arguments in the following order:
		1. If the message is a reply, assume entity_id is the replied to user
		2. Attempt to find the 1st and 2nd argument as a chat and/or user
		3. if none of the above conditions succeed, treat it all as reason text.

		if the chat ID is missing then assume the current chat the message was in.
	"""
	command = message.command
	command.pop(0)
	chat_id = message.chat.id
	entity_id = None
	reason = ""
	reasonstart = 0

	# Always assume the replied-to message is the intended user
	if not getattr(message.reply_to_message, 'empty', True):
		entity_id = message.reply_to_message.from_user.id

	entity0 = entity1 = None

	if len(command) >= 1:
		try:
			entity0, entit0_client = await get_entity(client, command[0])

			if type(entity0) != type(command[0]):
				if entity0.type in ["group", 'supergroup']:
					chat_id = entity0.id
				elif not entity_id:
					entity_id = entity0.id
				reasonstart += 1
		except:
			pass

		# only try to resolve the 2nd argument if we still don't have
		# the entity that we want to perform the action on.
		if len(command) >= 2 and not entity_id:
			try:
				entity1, entity1_client = await get_entity(client, command[1])
				if type(entity1) != type(command[1]):
					if not entity1.type in ["group", "supergroup"] and not entity_id:
						entity_id = entity1.id
						reasonstart += 1
			except:
				pass

	# we've resolved the entity_id and chat_id, lets get the reason.
	if command:
		reason = " ".join(command[reasonstart:])

	# validate we actually have everything resolved
	if not chat_id or not entity_id:
		await message.edit("<code>wtf are you trying to do??</code>")
		await asyncio.sleep(3)
		await message.delete()
		return None

	entity_id, entity_client = await get_entity(client, entity_id)
	chat_id, chat_client = await get_entity(client, chat_id)

	# make sure the user isn't an idiot.
	if entity_id.type != "private" or not chat_id.type in ["group", "supergroup"]:
		await message.edit(f"<code>You're doing something dumb. Stop it. Get some help! {entity_id.type} - {chat_id.type}</code>")
		await asyncio.sleep(3)
		await message.delete()
		return None

	return chat_id, entity_id, reason

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['promote'], prefixes=config['config']['prefixes']))
@log_errors
async def promote(client, message):
	if not await _CheckGroupAndPerms(message):
		return

	value = await _ParseCommandArguments(client, message)
	if value:
		chat_id, entity_id, reason = value

		if not await client.promote_chat_member(
			chat_id=chat_id.id,
			user_id=entity_id.id,
			can_change_info=False,
			can_post_messages=True,
			can_edit_messages=True,
			can_delete_messages=True,
			can_restrict_members=True,
			can_invite_users=True,
			can_pin_messages=True,
			can_promote_members=False
		):
			await message.edit("<code>I cannot promote that.</code>")
			await asyncio.sleep(3)
			await message.delete()
			return

		# log if we successfully promoted someone.
		chat_name = html.escape(chat_id.title)
		if message.chat.username:
			chat_name = f'<a href="https://t.me/{chat_id.username}">{chat_name}</a>'

		chat_text = '<b>Promotion Event</b>\n- <b>Chat:</b> ' + chat_name + '\n- <b>Promoted:</b> '
		user_text = entity_id.first_name
		if entity_id.last_name:
			user_text += f' {entity_id.last_name} <code>[{entity_id.id}]</code>'
		user = user_text = html.escape(user_text or 'Empty???')
		if entity_id.is_verified:
			user_text += ' <code>[VERIFIED]</code>'
		if entity_id.is_support:
			user_text += ' <code>[SUPPORT]</code>'
		if entity_id.is_scam:
			user_text += ' <code>[SCAM]</code>'
			user_text += f' [<code>{entity_id.id}</code>]'

		if reason and chat_id.type == "supergroup":
			# if they also have a title
			try:
				if not await client.set_administrator_title(
					chat_id=chat_id.id,
					user_id=entity_id.id,
					title=reason
				):
					await message.edit(f'<code>User was promoted but I cannot set their title to "{reason}"</code>')
				else:
					user_text += f"\n<b>Title:</b> <code>{html.escape(reason.strip()[:1000])}</code>"
			except:
				await message.edit(f'<code>User was promoted but I cannot set their title to "{reason}"</code>')
		await message.edit(f'<a href="https://t.me/{entity_id.username}">{user}</a><code> can now reign too!</code>')

		await log_chat(chat_text + user_text)
		await asyncio.sleep(3)
		await message.delete()

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['demote'], prefixes=config['config']['prefixes']))
@log_errors
async def demote(client, message):
	if not await _CheckGroupAndPerms(message):
		return

	value = await _ParseCommandArguments(client, message)
	if value:
		chat_id, entity_id, reason = value

		if not await client.promote_chat_member(
			chat_id=chat_id.id,
			user_id=entity_id.id,
			can_change_info=False,
			can_post_messages=False,
			can_edit_messages=False,
			can_delete_messages=False,
			can_restrict_members=False,
			can_invite_users=False,
			can_pin_messages=False,
			can_promote_members=False
		):
			await message.edit("<code>I cannot demote that.</code>")
			await asyncio.sleep(3)
			await message.delete()
			return

		# log if we successfully demoted someone.
		chat_name = html.escape(chat_id.title)
		if message.chat.username:
			chat_name = f'<a href="https://t.me/{chat_id.username}">{chat_name}</a>'

		chat_text = '<b>Demotion Event</b>\n- <b>Chat:</b> ' + chat_name + '\n- <b>Demoted:</b> '
		user_text = entity_id.first_name
		if entity_id.last_name:
			user_text += f' {entity_id.last_name} <code>[{entity_id.id}]</code>'
		user = user_text = html.escape(user_text or 'Empty???')
		if entity_id.is_verified:
			user_text += ' <code>[VERIFIED]</code>'
		if entity_id.is_support:
			user_text += ' <code>[SUPPORT]</code>'
		if entity_id.is_scam:
			user_text += ' <code>[SCAM]</code>'
			user_text += f' [<code>{entity_id.id}</code>]'

		await log_chat(chat_text + user_text)
		await message.edit(f'<a href="https://t.me/{entity_id.username}">{user}</a><code> is no longer king.</code>')
		await asyncio.sleep(3)
		await message.delete()

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['m', 'mute'], prefixes=config['config']['prefixes']))
@log_errors
async def mute(client, message):

	if not await _CheckGroupAndPerms(message):
		return

	value = await _ParseCommandArguments(client, message)
	if value:
		chat_id, entity_id, reason = value

		if is_admin(client, message, entity_id):
			await message.edit("<code>lol they're admin u tart.</code>")
			await asyncio.sleep(3)
			await message.delete()
			return

		if not await client.restrict_chat_member(
			chat_id=chat_id.id,
			user_id=entity_id.id,
			permissions=mute_permissions
		):
			await message.edit("<code>I cannot mute that.</code>")
			await asyncio.sleep(3)
			await message.delete()
			return

		# log if we successfully kicked someone.
		chat_name = html.escape(chat_id.title)
		if message.chat.username:
			chat_name = f'<a href="https://t.me/{chat_id.username}">{chat_name}</a>'

		chat_text = '<b>Mute Event</b>\n- <b>Chat:</b> ' + chat_name + '\n- <b>Muted:</b> '
		user_text = entity_id.first_name
		if entity_id.last_name:
			user_text += f' {entity_id.last_name} <code>[{entity_id.id}]</code>'
		user = user_text = html.escape(user_text or 'Empty???')
		if entity_id.is_verified:
			user_text += ' <code>[VERIFIED]</code>'
		if entity_id.is_support:
			user_text += ' <code>[SUPPORT]</code>'
		if entity_id.is_scam:
			user_text += ' <code>[SCAM]</code>'
			user_text += f' [<code>{entity_id.id}</code>]'
		chat_text += f'{user_text}\n- <b>Reason:</b> {html.escape(reason.strip()[:1000])}'

		await log_chat(chat_text)
		await message.edit(f'<a href="https://t.me/{entity_id.username}">{user}</a><code>\'s enter key was removed.</code>')
		await asyncio.sleep(3)
		await message.delete()

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['um', 'unmute'], prefixes=config['config']['prefixes']))
@log_errors
async def unmute(client, message):
	if not await _CheckGroupAndPerms(message):
		return

	value = await _ParseCommandArguments(client, message)
	if value:
		chat_id, entity_id, reason = value

		if is_admin(client, message, entity_id):
			await message.edit("<code>lol they're admin u tart.</code>")
			await asyncio.sleep(3)
			await message.delete()
			return

		if not await client.restrict_chat_member(
			chat_id=chat_id.id,
			user_id=entity_id.id,
			permissions=unmute_permissions
		):
			await message.edit("<code>I cannot unmute that.</code>")
			await asyncio.sleep(3)
			await message.delete()
			return

		# log if we successfully kicked someone.
		chat_name = html.escape(chat_id.title)
		if message.chat.username:
			chat_name = f'<a href="https://t.me/{chat_id.username}">{chat_name}</a>'

		chat_text = '<b>Mute Event</b>\n- <b>Chat:</b> ' + chat_name + '\n- <b>Muted:</b> '
		user_text = entity_id.first_name
		if entity_id.last_name:
			user_text += f' {entity_id.last_name} <code>[{entity_id.id}]</code>'
		user = user_text = html.escape(user_text or 'Empty???')
		if entity_id.is_verified:
			user_text += ' <code>[VERIFIED]</code>'
		if entity_id.is_support:
			user_text += ' <code>[SUPPORT]</code>'
		if entity_id.is_scam:
			user_text += ' <code>[SCAM]</code>'
			user_text += f' [<code>{entity_id.id}</code>]'
		chat_text += f'{user_text}\n- <b>Reason:</b> {html.escape(reason.strip()[:1000])}'

		await log_chat(chat_text)
		await message.edit(f'<a href="https://t.me/{entity_id.username}">{user}</a> <code>can now spam.</code>')
		await asyncio.sleep(3)
		await message.delete()

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['b', 'ban'], prefixes=config['config']['prefixes']))
@log_errors
async def banhammer(client, message):
	if not await _CheckGroupAndPerms(message):
		return

	value = await _ParseCommandArguments(client, message)
	print(value)
	if value:
		chat_id, entity_id, reason = value
		print(chat_id, "\n\n\n", entity_id)

		if is_admin(client, message, entity_id):
			await message.edit("<code>lol they're admin u tart.</code>")
			await asyncio.sleep(3)
			await message.delete()
			return

		# TODO: timed bans
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

		chat_text = '<b>Ban Event</b>\n- <b>Chat:</b> ' + chat_name + '\n- <b>Ban:</b> '
		user_text = entity_id.first_name
		if entity_id.last_name:
			user_text += f' {entity_id.last_name} <code>[{entity_id.id}]</code>'
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

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['ub', 'unban'], prefixes=config['config']['prefixes']))
@log_errors
async def unbanhammer(client, message):
	if not await _CheckGroupAndPerms(message):
		return

	value = await _ParseCommandArguments(client, message)
	if value:
		chat_id, entity_id, reason = value

		if is_admin(client, message, entity_id):
			await message.edit("<code>lol they're admin u tart.</code>")
			await asyncio.sleep(3)
			await message.delete()
			return

		await client.unban_chat_member(
			chat_id=chat_id.id,
			user_id=entity_id.id
		)

		# delete our kick command so pajeets don't try and run it themselves
		await message.delete()

		# log if we successfully kicked someone.
		chat_name = html.escape(chat_id.title)
		if message.chat.username:
			chat_name = f'<a href="https://t.me/{chat_id.username}">{chat_name}</a>'

		chat_text = '<b>Unban Event</b>\n- <b>Chat:</b> ' + chat_name + '\n- <b>Unban:</b> '
		user_text = entity_id.first_name
		if entity_id.last_name:
			user_text += f' {entity_id.last_name} <code>[{entity_id.id}]</code>'
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


@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['k', 'kick'], prefixes=config['config']['prefixes']))
@log_errors
async def kick(client, message):

	if not await _CheckGroupAndPerms(message):
		return

	value = await _ParseCommandArguments(client, message)
	if value:
		chat_id, entity_id, reason = value

		if is_admin(client, message, entity_id):
			await message.edit("<code>lol they're admin u tart.</code>")
			await asyncio.sleep(3)
			await message.delete()
			return

		await client.kick_chat_member(
			chat_id=chat_id.id,
			user_id=entity_id.id,
			until_date=int(time.time())
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
			user_text += f' {entity_id.last_name} <code>[{entity_id.id}]</code>'
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
'''{prefix}kick <i>[channel id|user id] [user id] [reason]</i> - Removes the user from the chat
Aliases: {prefix}k

{prefix}promote <i>[channel id|user id] [user id] [reason]</i> - Promotes the user to an administrator

{prefix}demote <i>[channel id|user id] [user id]</i> - Removes the user's administrator permissions

{prefix}mute <i>[channel id|user id] [user id]</i> - Prevent the user from sending any messages to the group
Aliases: {prefix}m

{prefix}unmute <i>[channel id|user id] [user id]</i> - Allow the user to send messages to the chat
Aliases: {prefix}um
''')
