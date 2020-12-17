import html, asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from .. import config, help_dict, get_entity, log_chat, log_errors, CheckAdmin, self_destruct, public_log_errors
from ..database import session, AutoScroll

f = filters.chat([])
initted = False

def __init_autoscroll():
    global initted
    if not initted:
        initted = True
        chats = session.query(AutoScroll).all()
        for a in chats:
            f.add(a.id)

__init_autoscroll()

@Client.on_message(f)
async def auto_read(client, message):
    __init_autoscroll()
    await client.read_history(message.chat.id)
    message.continue_propagation()

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['as', 'autoscroll'], prefixes=config['config']['prefixes']))
@log_errors
@public_log_errors
async def autoscroll(client, message):
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

    if chat.id in f:
        f.remove(chat.id)
        lel = session.query(AutoScroll).get(chat.id)
        if lel:
            session.delete(lel)
        await message.edit(f"<code>Autoscroll disabled in {chat.title}</code>")
    else:
        f.add(chat.id)
        lel = session.query(AutoScroll).get(chat.id)
        if not lel:
            session.add(AutoScroll(chat.id))
        await message.edit(f"<code>Autoscroll enabled in {chat.title}</code>")
    session.commit()
    await asyncio.sleep(3)
    await message.delete()


help_dict['moderation'] = ('Moderation',
'''{prefix}autoscroll <i>[channel id]</i> - Automatically mark chat messages as read
Aliases: {prefix}as
''')


