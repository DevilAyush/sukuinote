import html, asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from .. import config, help_dict, get_entity, log_chat, log_errors, CheckAdmin

f = filters.chat([])

@Client.on_message(f)
async def auto_read(client, message):
    await client.read_history(message.chat.id)
    message.continue_propagation()

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['as', 'autoscroll'], prefixes=config['config']['prefixes']))
@log_errors
async def autoscroll(client, message):
    if message.chat.id in f:
        f.remove(message.chat.id)
        await message.edit("<code>Autoscroll disabled</code>")
    else:
        f.add(message.chat.id)
        await message.edit("<code>Autoscroll enabled</code>")
    await asyncio.sleep(3)
    await message.delete()


help_dict['moderation'] = ('Moderation',
'''{prefix}autoscroll <i>[channel id]</i> - Automatically mark chat messages as read
Aliases: {prefix}as
''')


