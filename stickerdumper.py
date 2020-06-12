from io import BytesIO
from .. import loader, utils

from asyncio import sleep


@loader.tds
class StickerDumperMod(loader.Module):
    """Description for module"""
    strings = {"name": "StickerDumper"}
        
    async def getstkrcmd(self, message):
        f = BytesIO()
        f.name="sticker.jpg"
        reply = await message.get_reply_message()
        await reply.download_media(f)
        f.seek(0)
        await utils.answer(message, f)