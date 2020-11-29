import html
import asyncio
import unidecode
import logging
from pyrogram import Client, filters
from .. import config, slave, log_errors, app_user_ids, log_chat

# I feel I should explain why this module exists:
# No one who shares this kind of content should be
# able to roam around free of bans. This code
# brings it to my attention so I can suggest blacklisting
# in spb and thus not allowing these types of people
# to get away with this sick and disgustingness.

suspiciouswords = ["cp", "young", "desi", "rape", "children", "child"]

@Client.on_message(filters.chat([-1001252771625]))
@log_errors
async def log_forwards(client, message):
	if not config['config'].get('log_spb_cacp'):
		return
	
	try:
		# Parse SPB's log message
		chunks = message.text.split("\n\n")
		mtype = chunks[0]
		mcontent = message.text.split("===== CONTENT =====")[1]
		# Only check predictions
		if mtype == "#spam_prediction":
			# parse the header
			mheader = {}
			for h in chunks[1].split("\n"):
				ch = h.split(": ")
				header[ch[0]] = ch[1]
			
			# Spammers like to try and do weird shit to avoid detection
			# lets try and clean the text up a bit and maybe make things 
			# easier to compare with, starting by stripping diacritics
			# and other unicode nonsense.
			cleanstr = unidecode.unidecode(mcontent)

			# now remove all the different punctuation marks and any other
			# nonsense they may have added
			printable = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "
			content = filter(lambda x: x in printable, cleanstr)

			# Check for suspicious words.
			for word in suspiciouswords:
				if word in mcontent.lower():
					ptid = header["Private Telegram ID"]
					mhash = header["Message Hash"]
					await log_chat(f'<b>CACP Event</b>\n- <b>PTID:</b> {ptid}\n- <b>Message Hash:</b> {mhash}\n<a href="https://t.me/SpamProtectionLogs/{message.message_id}">Logged Message</a>')

	except Exception as e:
		# we don't really care if this fails
		logging.warning(str(e))
		pass