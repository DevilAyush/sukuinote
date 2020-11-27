import asyncio

from pyrogram import Client, filters
from pyrogram.methods.chats.get_chat_members import Filters as ChatMemberFilters
from pyrogram.types import Message
from .. import config, help_dict, log_errors, get_entity, _ParseCommandArguments

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['add'], prefixes=config['config']['prefixes']))
@log_errors
async def add_user(client, message: Message):
	
	value = await _ParseCommandArguments(client, message)
	if value:
		chat_id, entity_id, reason = value

		# TODO: maybe support adding multiple people?
		if await client.add_chat_members(chat_id.id, entity_id.id):
			await message.edit(f"<code>Successfully added to {chat_id.title}</code>")
		else:
			await message.edit(f"<code>Failed to add {entity_id.title} to {chat_id.title}</code>")
		await asyncio.sleep(3)
		await message.delete()


help_dict['add'] = ('Add',
'''{prefix}add <i>(maybe reply to a message)</i> - Adds the user to a chat (either via a reply or in the chat itself)''')