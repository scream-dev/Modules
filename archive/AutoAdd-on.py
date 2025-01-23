#           __..--''``---....___   _..._    __
# /// //_.-'    .-/";  `        ``<._  ``.''_ `. / // /
#///_.-' _..--.'_    \                    `( ) ) // //
#/ (_..-' // (< _     ;_..__               ; `' / ///
# / // // //  `-._,_)' // / ``--...____..-' /// / //
# 🐈 Module writed @ScreamDev 
# 👌 Channel @ScreamModules
# 🧨 Blog: @ScreamDevBlog

# meta developer: @ScreamDev
# meta banner: https://raw.githubusercontent.com/scream-dev/Modules/refs/heads/main/images/AutoAddon.png
# meta pic: https://raw.githubusercontent.com/scream-dev/Modules/refs/heads/main/images/AutoAddon.png

import asyncio

from .. import loader, utils


@loader.tds
class AutoEdit(loader.Module):
    """Добавляет к сообщению канала ватемарку"""

    strings = {
        "name": "AutoEdit",
        "timechoice": "Время, за которое будет редактироваться сообщение.(в секундах)",
        "editmsg": "Текст, на который будет редактироваться ваше сообщение.",
    }

    @loader.watcher(out=True)
    async def watcher(self, message):
        if self.get("autoedit"):
            if message.text == "<b><i>AutoEdit on.</i></b>":
                return
            if message.text == "@DorotoroMods":
                return
            if message.text == "@AstroModules":
                return

            await asyncio.sleep(self.config["timechoice"])
            await message.edit(self.config["editmsg"])

    async def client_ready(self, client, db):
        self._db = db
        self._me = await client.get_me()

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "timechoice", "10", doc=lambda: self.strings("timechoice")
            ),
            loader.ConfigValue(
                "editmsg",
                "<b>========\nЗасекречено</b>",
                doc=lambda: self.strings("editmsg"),
            ),
        )

    @loader.command()
    async def autoedit(self, message):
        "- включить/выключить AutoEdit."
        if self.get("autoedit") == True:
            self.set("autoedit", False)
            await utils.answer(message, "<b><i>AutoEdit off.</i></b>")
            return
        elif self.get("autoedit") == False or self.get("autoedit") is None:
            self.set("autoedit", True)
            await utils.answer(message, "<b><i>AutoEdit on.</i></b>")
