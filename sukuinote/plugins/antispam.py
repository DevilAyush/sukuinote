import html
import asyncio
import unidecode
import logging
from unidecode import unidecode
from pyrogram import Client, filters
from .. import config, slave, log_errors, app_user_ids, log_chat, get_entity, self_destruct, database, CheckAdmin, public_log_errors

DEBUG = False

if DEBUG:
	spamreportchats = [-1001450488581]
else:
	spamreportchats = filters.chat([-1001426404283])

spamkeywords = ["Teleagram", "Teleagram members Private", "group Promotio", "add members", "telegram", "Promotio", "contact"]

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['fspam'], prefixes=config['config']['prefixes']))
@log_errors
@public_log_errors
async def fspam(client, message):
	if not getattr(message.reply_to_message, 'empty', True):
		for chat in spamreportchats:
			await client.forward_messages(chat_id=chat, from_chat_id=message.reply_to_message.chat.id, message_ids=[message.reply_to_message.message_id], disable_notification=True)
	await message.delete()

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['autoban'], prefixes=config['config']['prefixes']))
@log_errors
@public_log_errors
async def autoban(client, message):
	command = message.command
	command.pop(0)
	chat = message.chat.id
	if command:
		chat = command[0]
	
	try:
		chat, entity_client = await get_entity(client, chat)
	except:
		await self_destruct("<code>Invalid chat or group</code>")
		return

	l = database.session.query(database.AutoBanSpammers).get(chat.id)

	if l:
		database.session.delete(l)
		database.session.commit()
		await message.edit(f"<code>Automatic banning disabled in {chat.title}</code>")
	else:
		l = database.AutoBanSpammers(id=chat.id)
		database.session.add(l)
		database.session.commit()
		await message.edit(f"<code>Automatic banning enabled in {chat.title}</code>")
	await asyncio.sleep(3)
	await message.delete()

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.new_chat_members)
@log_errors
async def anti_join_spammer(client, message):
	spampoints = 0

	entity = await get_entity(client, message.from_user.id)
	name = entity.first_name + " " + entity.last_name
	# U+0420 CYRILLIC CAPITAL LETTER ER (https://fileformat.info/info/unicode/char/420)
	# Replace the cyrillic R with a P, these spammers think they're cute.
	spampoints += 1 if "\u0420" in name else 0
	# U+2640 FEMALE SIGN (https://fileformat.info/info/unicode/char/2640)
	# Check if their name has the female sign
	spampoints += 1 if "\u2640" in name else 0
	# Normalize their name and check for spammy keywords
	name = unidecode(name.replace("\u0420", "P")).replace("  ", " ")
	for keyword in spamkeywords:
		if keyword.lower() in name.lower():
			spampoints += 1

	if spampoints >= 5:
		link = ""
		if not getattr(message.chat.username, 'empty', True):
			link = f'<a href="https://t.me/{message.chat.username}">{html.escape(message.chat.title)}</a>'
		else:
			link = html.escape(message.chat.title)
		link += " [{message.chat.id}]"
		name = html.escape(entity.first_name + " " + entity.last_name)
		await log_chat(f'<b>Spammer Join Event</b>\n- <b>Chat:</b> {link}\n- <b>Joined User:</b> {name}')
		if database.session(database.AutoBanSpammers).get(message.chat.id):
			if CheckAdmin(message):
				message.reply("/ban likely spammer [automated]")

