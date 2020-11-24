import asyncio

from pyrogram import Client, filters
from pyrogram.methods.chats.get_chat_members import Filters as ChatMemberFilters
from pyrogram.types import Message
from .. import config, help_dict, log_errors, get_entity

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['add'], prefixes=config['config']['prefixes']))
@log_errors
async def add_user(client, message: Message):
	command = message.command
	command.pop(0)
	chat_id = message.chat.id
	entity_id = command
	reason = ""

	if len(command) >= 2:
		# -1001450488581 @rDakotaBot
		try:
			noob = int(command[0])
			if noob > 0:
				entity_id = noob
			else:
				chat_id = noob
		except ValueError:
			# assume it's a channel name.
			chat_id = command[0]
		
		# now for arg 2
		try:
			noob = int(command[1])
			if noob > 0:
				entity_id = noob
			else:
				chat_id = noob
		except ValueError:
			# assume it's an entity name.
			entity_id = command[1]
		
	elif len(command) == 1:
		# They replied to the message with -add @ChatName
		if not getattr(message.reply_to_message, 'empty', True):
			entity_id = message.reply_to_message.from_user.id
			chat_id = command[0]
		else: # They sent -add @username
			entity_id = command[0]
	else:
		# what the fuck
		await message.edit("<code>Yea? And where am I gonna be adding them, huh?</code>")
		await asyncio.sleep(3)
		await message.delete()
		return

	# Attempt to resolve
	entity_id, entity_client = await get_entity(client, entity_id)
	chat_id, chat_client = await get_entity(client, chat_id)

	if entity_id.type != "private" or not chat_id.type in ["group", "supergroup"]:
		await message.edit("<code>You're doing something dumb. Stop it. Get some help!</code>")
		await asyncio.sleep(3)
		await message.delete()
		return

	# TODO: maybe support adding multiple people?
	if await client.add_chat_members(chat_id.id, entity_id.id):
		await message.edit(f"<code>Successfully added to {chat_id.title}</code>")
	else:
		await message.edit(f"<code>Failed to add {entity_id.title} to {chat_id.title}</code>")
	await asyncio.sleep(3)
	await message.delete()


help_dict['add'] = ('Add',
'''{prefix}add <i>(maybe reply to a message)</i> - Adds the user to a chat (either via a reply or in the chat itself)''')