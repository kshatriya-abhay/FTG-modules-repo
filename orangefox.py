# -*- coding: future_fstrings -*-

#    Friendly Telegram (telegram userbot)
#    Copyright (C) 2018-2019 The Authors
#    Copyright (C) 2018-2020 OrangeFox Recovery

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

import aiohttp
import json

from .. import loader, utils


API_HOST = "https://api.orangefox.tech/"


def register(cb):
    cb(OrangeFoxMod())


async def send_request(api_method):
    async with aiohttp.ClientSession() as session:
        async with session.get(API_HOST + api_method) as response:
            text = await response.text()
            return json.loads(text)


@loader.tds
class OrangeFoxMod(loader.Module):
    strings = {
        "name": "OrangeFox Recovery",
        "list_devices_stable_header": "<b>List of supported devices with stable releases:</b>",
        "no_such_device": "No such device is found!"
    }

    def config_complete(self):
        self.name = self.strings["name"]

    async def ofoxcmd(self, message):
        """Get"s last OrangeFox releases"""
        devices = await send_request("list_devices/")
        args = utils.get_args(message)
        if not args:
            text = self.strings["list_devices_stable_header"]
            codenames = await send_request("available_stable_releases/")

            for device in devices:
                if device["codename"] not in codenames:
                    continue

                text += f"\n- {device['fullname']} (<code>{device['codename']}</code>)"

            await utils.answer(message, text)
            return

        codename = args[0].lower()
        if codename not in [a["codename"] for a in devices]:
            await utils.answer(message, self.strings["no_such_device"])
            return

        release = await send_request("last_stable_release/" + codename)
        device = await send_request("details/" + codename)
        maintained = ""

        if device["maintained"] == 1:
            maintained = f"<b>Maintainer:</b> {device['maintainer']}, Maintained"
        elif device["maintained"] == 2:
            maintained = f"<b>Maintainer:</b> {device['maintainer']}, Maintained without having device on hands"
        elif device["maintained"] == 3:
            maintained = f"⚠️ <b>Not maintained!</b> Previous maintainer: {device['maintainer']}"

        text = f"<b>Latest OrangeFox Recovery stable release</b>"
        text += f"\n<b>Device:</b> {device['fullname']} (<code>{device['codename']}</code>)"
        text += f"\n<b>Version:</b> <code>{release['version']}</code>"
        text += f"\n<b>Release date:</b> " + release["date"]
        text += f"\n{maintained}"
        text += f"\n<b>File:</b> <code>{release['file_name']}</code>: {release['size_human']}"
        text += f"\n<b>File MD5:</b> <code>{release['md5']}</code>"

        if "notes" in release:
            text += "\n\n📝 <b>Build notes:</b>\n"
            text += release["notes"]

        text += f"\n<a href=\"{release['url']}\">Download</a>"
        if "sf" in release:
            text += f" | <a href=\"{release['sf']['url']}\">Mirror</a>"

        await utils.answer(message, text)

    async def client_ready(self, client, db):
        self.client = client
