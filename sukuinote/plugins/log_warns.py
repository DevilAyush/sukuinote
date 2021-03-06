import html
import asyncio
from pyrogram import Client, filters
from pyrogram.errors.exceptions.flood_420 import FloodWait
from .. import config, slave, log_errors

warned = set()
lock = asyncio.Lock()

@Client.on_message(~filters.chat(config['config']['log_chat']) & filters.regex(r'^[/!](?:[d]*warn?)(?:$|\W+)') & filters.group)
@log_errors
async def log_warn(client, message):
	if not config['config']['log_warns']:
		return

	# 1087968824 is @GroupAnonymousBot
	if getattr(message.sender_chat, 'empty', True):
		if message.from_user.is_bot:
			return

	# Ignore the slave forwards
	if not getattr(message.forward_from, 'empty', True):
		if message.forward_from.id == (await slave.get_me()).id:
			return

	identifier = (message.chat.id, message.message_id)
	async with lock:
		if identifier in warned:
			return
		chat_text = html.escape(message.chat.title)
		if message.chat.username:
			chat_text = f'<a href="https://t.me/{message.chat.username}">{chat_text}</a>'
		text = f'<b>Warn Event</b>\n- <b>Chat:</b> {chat_text} '
		if message.chat.is_verified:
			chat_text += '<code>[VERIFIED]</code> '
		if message.chat.is_support:
			chat_text += '<code>[SUPPORT]</code> '
		if message.chat.is_scam:
			chat_text += '<code>[SCAM]</code> '
		text += f'[<code>{message.chat.id}</code>]\n- <b>Warner:</b> '
		if message.from_user:
			user_text = message.from_user.first_name
			if message.from_user.last_name:
				user_text += f' {message.from_user.last_name}'
			user_text = '<code>[DELETED]</code>' if message.from_user.is_deleted else html.escape(user_text or 'Empty???')
			if message.from_user.is_verified:
				user_text += ' <code>[VERIFIED]</code>'
			if message.from_user.is_support:
				user_text += ' <code>[SUPPORT]</code>'
			if message.from_user.is_scam:
				user_text += ' <code>[SCAM]</code>'
			user_text += f' [<code>{message.from_user.id}</code>]'
		elif message.sender_chat and message.sender_chat.id != message.chat.id:
			user_text = html.escape(message.sender_chat.title)
			if message.sender_chat.username:
				user_text = f'<a href="https://t.me/{message.sender_chat.username}">{user_text}</a>'
			if message.sender_chat.is_verified:
				user_text += ' <code>[VERIFIED]</code>'
			if message.sender_chat.is_support:
				user_text += ' <code>[SUPPORT]</code>'
			if message.sender_chat.is_scam:
				user_text += ' <code>[SCAM]</code>'
		else:
			user_text = 'Anonymous'
		text += f'{user_text}\n'
		start, end = message.matches[0].span()
		text += f'- <b><a href="{message.link}">Warn Message'
		mtext = (message.text or message.caption or '').strip()
		if start or end < len(mtext):
			text += ':'
		text += '</a></b>'
		if start or end < len(mtext):
			text += f' {html.escape(mtext.strip()[:1000])}'
		reply = message.reply_to_message
		if not getattr(reply, 'empty', True):
			text += '\n- <b>Warnee:</b> '
			if reply.from_user:
				user_text = reply.from_user.first_name
				if reply.from_user.last_name:
					user_text += f' {reply.from_user.last_name}'
				user_text = '<code>[DELETED]</code>' if reply.from_user.is_deleted else html.escape(user_text or 'Empty???')
				if reply.from_user.is_verified:
					user_text += ' <code>[VERIFIED]</code>'
				if reply.from_user.is_support:
					user_text += ' <code>[SUPPORT]</code>'
				if reply.from_user.is_scam:
					user_text += ' <code>[SCAM]</code>'
				user_text += f' [<code>{reply.from_user.id}</code>]'
			else:
				user_text = 'None???'
			text += f'{user_text}\n- <b><a href="{reply.link}">Warned Message'
			mtext = reply.text or reply.caption or ''
			if mtext.strip():
				text += ':'
			text += f'</a></b> {html.escape(mtext.strip()[:1000])}'
		while True:
			try:
				reply = await slave.send_message(config['config']['log_chat'], text, disable_web_page_preview=True)
			except FloodWait as ex:
				await asyncio.sleep(ex.x + 1)
			else:
				break
		warned.add(identifier)
		warned.add((reply.chat.id, reply.message_id))
