import asyncio, arrow
from currency_converter import CurrencyConverter
from pyrogram import Client, filters
from unitconvert import lengthunits, massunits, volumeunits
from .. import config, help_dict, get_entity, log_chat, log_errors, self_destruct

c = CurrencyConverter()

# For converting
def convert_f(fahrenheit):
	f = float(fahrenheit)
	f = (f * 9 / 5) + 32
	return f


def convert_c(celsius):
	cel = float(celsius)
	cel = (cel - 32) * 5 / 9
	return cel


@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['curr'], prefixes=config['config']['prefixes']))
@log_errors
async def currency(client, message):
	if len(message.command) <= 3:
		await self_destruct(message, "<code>Incorrect Syntax</code>")
		return

	value = message.command[1]
	curr1 = message.command[2].upper()
	curr2 = message.command[3].upper()
	try:
		conv = c.convert(int(value), curr1, curr2)
		await message.edit(f"<code>{value} {curr1} = {conv:,.2f} {curr2}</code>")
	except ValueError as err:
		await self_destruct(message, f"<code>{str(err)}</code>")

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['length'], prefixes=config['config']['prefixes']))
@log_errors
async def length(client, message):
	if len(message.command) <= 3:
		await self_destruct(message, "<code>Incorrect Syntax</code>")
		return

	value = message.command[1]
	curr1 = message.command[2].lower()
	curr2 = message.command[3].lower()
	try:
		conv = lengthunits.LengthUnit(float(value), curr1, curr2).doconvert()
		await message.edit(f"<code>{value} {curr1} = {conv:,.2f} {curr2}</code>")
	except ValueError as err:
		await self_destruct(message, f"<code>{str(err)}</code>")

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['mass'], prefixes=config['config']['prefixes']))
@log_errors
async def mass(client, message):
	if len(message.command) <= 3:
		await self_destruct(message, "<code>Incorrect Syntax</code>")
		return

	value = message.command[1]
	curr1 = message.command[2].lower()
	curr2 = message.command[3].lower()
	try:
		conv = massunits.MassUnit(float(value), curr1, curr2).doconvert()
		await message.edit(f"<code>{value} {curr1} = {conv:,.2f} {curr2}</code>")
	except ValueError as err:
		await self_destruct(message, f"<code>{str(err)}</code>")

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['vol', 'volume'], prefixes=config['config']['prefixes']))
@log_errors
async def volume(client, message):
	if len(message.command) <= 3:
		await self_destruct(message, "<code>Incorrect Syntax</code>")
		return

	value = message.command[1]
	curr1 = message.command[2].lower()
	curr2 = message.command[3].lower()
	try:
		conv = volumeunits.VolumeUnit(float(value), curr1, curr2).doconvert()
		await message.edit(f"<code>{value} {curr1} = {conv:,.2f} {curr2}</code>")
	except ValueError as err:
		await self_destruct(message, f"<code>{str(err)}</code>")

@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['temp'], prefixes=config['config']['prefixes']))
@log_errors
async def temperature(client, message):
	if len(message.text.split()) <= 2:
		await self_destruct(message, "<code>Incorrect Syntax</code>")
		return
	
	temp1 = message.command[1]
	temp2 = message.command[2]
	text = None
	try:
		if temp2 == "F":
			result = convert_c(temp1)
			text = f"<code>{temp1}°F</code> = <code>{result:,.2f}°C</code>"
		elif temp2 == "C":
			result = convert_f(temp1)
			text = f"<code>{temp1}°C</code> = <code>{result:,.2f}°F</code>"
		else:
			text = f"Unknown type {temp2}"
	except ValueError as err:
		await self_destruct(message, f"<code>{str(err)}</code>")
		return

	await message.edit(text)


@Client.on_message(~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['time'], prefixes=config['config']['prefixes']))
@log_errors
async def calc_time(client, message):

	try:
		command = message.command
		command.pop(0)
		if command:
			tz = " ".join(command)
		elif not config['config']['timezone']:
			await message.delete()
			return
		else:
			tz = config['config']['timezone']

		now = arrow.utcnow().to(tz)
		time = now.format("hh:mm A (HH:mm)")
		date = now.format(r"MM-DD-YYYY")

		await message.edit(f"<i>Currently it is <b>{time}</b> on <b>{date}</b> in <b>{now.format('ZZZ')}</b></i>")
	except ValueError as e:
		await self_destruct(message, f"<code>{str(e)}</code>")

help_dict["calculator"] = ('Calculator',
'''{prefix}curr <i>[value] [from currency] [to currency]</i> - Convert source currency to dest currency

{prefix}temp <i>[temp] [C|F]</i> - Convert the source temp to dest

{prefix}time <i>[TZ database name]</i> - Get the time in the timezone
''')