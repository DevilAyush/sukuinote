import os
import html
import time
import logging
import asyncio
import traceback
import functools
import yaml
import aiohttp
from time import sleep
from datetime import timedelta
from pyrogram import Client, StopPropagation, ContinuePropagation
from pyrogram.types import Chat, User, Message
from pyrogram.parser import parser
from pyrogram.methods.chats.get_chat_members import Filters as ChatMemberFilters
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid, ChannelInvalid

logging.basicConfig(level=logging.INFO)
with open('config.yaml') as config:
    config = yaml.safe_load(config)
loop = asyncio.get_event_loop()
help_dict = dict()

apps = []
app_user_ids = dict()
# this code here exists because i can't be fucked
class Parser(parser.Parser):
    async def parse(self, text, mode):
        if mode == 'through':
            return text
        return await super().parse(text, mode)
for session_name in config['config']['sessions']:
    app = Client(session_name, api_id=config['telegram']['api_id'], api_hash=config['telegram']['api_hash'], plugins={'root': os.path.join(__package__, 'plugins')}, parse_mode='html', workdir='sessions')
    app.parser = Parser(app)
    apps.append(app)
slave = Client('sukuinote-slave', api_id=config['telegram']['api_id'], api_hash=config['telegram']['api_hash'], plugins={'root': os.path.join(__package__, 'slave-plugins')}, parse_mode='html', bot_token=config['telegram']['slave_bot_token'], workdir='sessions')
slave.parser = Parser(slave)
session = aiohttp.ClientSession()

async def get_entity(client, entity):
    entity_client = client
    if not isinstance(entity, Chat):
        try:
            entity = int(entity)
        except ValueError:
            pass
        except TypeError:
            entity = entity.id
        try:
            entity = await client.get_chat(entity)
        except (PeerIdInvalid, ChannelInvalid):
            for app in apps:
                if app != client:
                    try:
                        entity = await app.get_chat(entity)
                    except (PeerIdInvalid, ChannelInvalid):
                        pass
                    else:
                        entity_client = app
                        break
            else:
                entity = await slave.get_chat(entity)
                entity_client = slave
    return entity, entity_client

async def get_user(client, entity):
    entity_client = client
    if not isinstance(entity, User):
        try:
            entity = int(entity)
        except ValueError:
            pass
        except TypeError:
            entity = entity.id
        try:
            entity = await client.get_users(entity)
        except PeerIdInvalid:
            for app in apps:
                if app != client:
                    try:
                        entity = await app.get_users(entity)
                    except PeerIdInvalid:
                        pass
                    else:
                        entity_client = app
                        break
            else:
                entity = await slave.get_users(entity)
                entity_client = slave
    return entity, entity_client

async def log_chat(message):
    await slave.send_message(config['config']['log_chat'], message, disable_web_page_preview=True)

async def is_admin(client, message, entity):
    # Here lies the sanity checks
    admins = await client.get_chat_members(
        message.chat.id, filter=ChatMemberFilters.ADMINISTRATORS
    )
    admin_ids = [user.user.id for user in admins]
    return entity.id in admin_ids

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
	if not entity_id.type in ["private", "bot"] or not chat_id.type in ["group", "supergroup"]:
		await message.edit(f"<code>You're doing something dumb. Stop it. Get some help! {entity_id.type} - {chat_id.type}</code>")
		await asyncio.sleep(3)
		await message.delete()
		return None

	return chat_id, entity_id, reason

async def CheckAdmin(message: Message):
    """Check if we are an admin."""
    admin = "administrator"
    creator = "creator"
    ranks = [admin, creator]

    SELF = await app.get_chat_member(
        chat_id=message.chat.id, user_id=message.from_user.id
    )

    if SELF.status not in ranks:
        await message.edit("<code>I am not an admin here lmao. What am I doing?</code>")
        sleep(2)
        await message.delete()

    else:
        if SELF.status is not admin or SELF.can_restrict_members:
            return True
        else:
            await message.edit("<code>No Permissions to restrict Members</code>")
            sleep(2)
            await message.delete()

def log_errors(func):
    @functools.wraps(func)
    async def wrapper(client, *args):
        try:
            await func(client, *args)
        except (StopPropagation, ContinuePropagation):
            raise
        except Exception:
            tb = traceback.format_exc()
            try:
                await slave.send_message(config['config']['log_chat'], f'Exception occured in <code>{func.__name__}\n\n{html.escape(tb)}</code>', disable_web_page_preview=True)
            except Exception:
                logging.exception('Failed to log exception for %s as slave', func.__name__)
                tb = traceback.format_exc()
                for app in apps:
                    try:
                        await app.send_message(config['config']['log_chat'], f'Exception occured in <code>{func.__name__}\n\n{html.escape(tb)}</code>', disable_web_page_preview=True)
                    except Exception:
                        logging.exception('Failed to log exception for %s as app', func.__name__)
                        tb = traceback.format_exc()
                    else:
                        break
                raise
            raise
    return wrapper

def public_log_errors(func):
    @functools.wraps(func)
    async def wrapper(client, message):
        try:
            await func(client, message)
        except (StopPropagation, ContinuePropagation):
            raise
        except Exception:
            await message.reply_text("<code>" + html.escape(traceback.format_exc()) + "</code>", disable_web_page_preview=True)
            raise
    return wrapper

# https://stackoverflow.com/a/49361727
def format_bytes(size):
    size = int(size)
    # 2**10 = 1024
    power = 1024
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]+'B'}"

# https://stackoverflow.com/a/34325723
def return_progress_string(current, total):
    filled_length = int(30 * current // total)
    return '[' + '=' * filled_length + ' ' * (30 - filled_length) + ']'

# https://stackoverflow.com/a/852718
# https://stackoverflow.com/a/775095
def calculate_eta(current, total, start_time):
    if not current:
        return '00:00:00'
    end_time = time.time()
    elapsed_time = end_time - start_time
    seconds = (elapsed_time * (total / current)) - elapsed_time
    thing = ''.join(str(timedelta(seconds=seconds)).split('.')[:-1]).split(', ')
    thing[-1] = thing[-1].rjust(8, '0')
    return ', '.join(thing)

progress_callback_data = dict()
async def progress_callback(current, total, reply, text, upload):
    message_identifier = (reply.chat.id, reply.message_id)
    last_edit_time, prevtext, start_time = progress_callback_data.get(message_identifier, (0, None, time.time()))
    if current == total:
        try:
            progress_callback_data.pop(message_identifier)
        except KeyError:
            pass
    elif (time.time() - last_edit_time) > 1:
        handle = 'Upload' if upload else 'Download'
        if last_edit_time:
            speed = format_bytes((total - current) / (time.time() - start_time))
        else:
            speed = '0 B'
        text = f'''{text}
<code>{return_progress_string(current, total)}</code>

<b>Total Size:</b> {format_bytes(total)}
<b>{handle}ed Size:</b> {format_bytes(current)}
<b>{handle} Speed:</b> {speed}/s
<b>ETA:</b> {calculate_eta(current, total, start_time)}'''
        if prevtext != text:
            await reply.edit_text(text)
            prevtext = text
            last_edit_time = time.time()
            progress_callback_data[message_identifier] = last_edit_time, prevtext, start_time
