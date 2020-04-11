# -*- coding: future_fstrings -*-

#    Friendly Telegram (telegram userbot)
#    Copyright (C) 2018-2019 The Authors

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import telethon

from .. import loader, utils


def register(cb):
    cb(RecentActionsMod())


@loader.tds
class RecentActionsMod(loader.Module):
    """Reads recent actions"""
    strings = {"name": "Recent Actions",
               "reply_start": "<code>Reply to a message to specify where to start</code>",
               "invalid_chat": "<code>This isn't a supergroup or channel",
               "needs_admin": "<code>Admin rights are required to read deleted messages</code>",
               "recovered": "Deleted message {} recovered. Originally sent at {} by {}, deleted at {} by {}"}

    def __init__(self):
        self.name = self.strings["name"]

    async def recoverdeletedcmd(self, message):
        """Restores deleted messages sent after replied message (optionally specify how many to recover)"""
        msgs = message.client.iter_admin_log(message.to_id, delete=True)
        if not message.is_reply:
            await utils.answer(message, self.strings["reply_start"])
            return
        if not isinstance(message.to_id, telethon.tl.types.PeerChannel):
            await utils.answer(message, self.strings["invalid_chat"])
            return
        target = (await message.get_reply_message()).date
        ret = []
        try:
            async for msg in msgs:
                if msg.original.date < target:
                    break
                if msg.original.action.message.date < target:
                    continue
                ret += [msg]
        except telethon.errors.rpcerrorlist.ChatAdminRequiredError:
            await utils.answer(message, self.strings["needs_admin"])
        args = utils.get_args(message)
        if len(args) > 0:
            try:
                count = int(args[0])
                ret = ret[-count:]
            except ValueError:
                pass
        for msg in reversed(ret):
            orig = msg.original.action.message
            deldate = msg.original.date.isoformat()
            origdate = orig.date.isoformat()
            await message.respond(self.strings["recovered"].format(msg.id, origdate, orig.from_id,
                                                                   deldate, msg.user_id))
            if isinstance(orig, telethon.tl.types.MessageService):
                await message.respond("<code>" + utils.escape_html(orig.stringify()) + "</code>")
            else:
                await message.respond(orig)
