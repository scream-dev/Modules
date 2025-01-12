#           __..--''``---....___   _..._    __
# /// //_.-'    .-/";  `        ``<._  ``.''_ `. / // /
#///_.-' _..--.'_    \                    `( ) ) // //
#/ (_..-' // (< _     ;_..__               ; `' / ///
# / // // //  `-._,_)' // / ``--...____..-' /// / //
# 🐈 Module writed @ScreamDev 
# 👌 Channel @ScreamModules
# 🧨 Blog: @ScreamDevBlog
# meta developer: @ScreamDev, yg_modules

import random as r
import requests
import asyncio
from telethon.tl.types import Message
from yumlib import yummy

from .. import loader, utils

class yg_crypto(loader.Module):
    """Модуль для того чтобы узнать курс крипты/фиата"""

    strings = {
        "name": "yg_crypto",
        "inc_args": "<b>🐳 Incorrect args</b>",
        "keyerror": (
            "🗿 <b>Maybe the coin is not in the site database or you typed the wrong"
            " name.</b>"
        ),
        "okey": "<b>👯 Successfully. Current default valute: {}</b>",
        "stopped": "<b>🛑 The currency update has been stopped.</b>",
    }
    
    strings_ru = {
        "inc_args": "<b><emoji document_id=5348140027698227662>🙀</emoji> Неккоректные аргументы</b>",
        "keyerror": (
            "<b><emoji document_id=5348140027698227662>🙀</emoji> Возможно монеты нету в базе данных сайта, или вы ввели неккоректное"
            " название.</b>"
        ),
        "okey": "<b><emoji document_id=5348140027698227662>🙀</emoji> Успешно. Текущая стандартная валюта: {}</b>",
        "stopped": "<b><emoji document_id=5348140027698227662>🛑</emoji> Обновление курса остановлено.</b>"
    }

    def __init__(self):
        self.running = False
        self.update_task = None

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        await yummy(client)

        if "defaultvalute" not in self.db:
            self.db.set("defaultvalute", "val", "btc")

    async def монетаcmd(self, message: Message):
        """<название> выбрать крипту по умолчанию"""

        args = utils.get_args_raw(message)
        self.db.set("defaultvalute", "val", args)
        await utils.answer(message, self.strings["okey"].format(args))

    async def курсcmd(self, message: Message):
        """<кол-во> <название монеты> смотреть курс"""
        args = utils.get_args_raw(message)
        tray = self.db.get("defaultvalute", "val", args)
        if tray == "":
            tray = "btc"
        if not args:
            args = "1" + " " + str(tray)
        args_list = args.split(" ")
        try:
            if len(args_list) == 1 and isinstance(float(args_list[0]), float):
                args_list.append(str(tray))
        except Exception:
            args_list = ["1", args_list[0]]
        coin = args_list[1].upper()

        if coin == "ТОН":
            coin = "TON"
        if coin == "ЮСД":
            coin = "USD"
        if coin == "РУБ":
            coin = "RUB"
        if coin == "ГРН":
            coin = "UAH"
        if coin == "ЗЛ":
            coin = "PLN"

        self.running = True
        self.message_id = message.id  # Сохранение ID сообщения для обновления
        if self.update_task is None:
            self.update_task = self.client.loop.create_task(self.update_currency(message, args_list[0], coin))

    async def update_currency(self, message: Message, count: str, coin: str):
        while self.running:
            api = requests.get(
                f"https://min-api.cryptocompare.com/data/price?fsym={coin}&tsyms=USD,RUB,UAH,PLN,KZT,BTC,ETH,TON"
            ).json()
            smiles = r.choice(
                [
                    "<emoji document_id=5348140027698227662>🙀</emoji>",
                    "<emoji document_id=5348175255019988816>🙀</emoji>",
                    "<emoji document_id=5348179601526892213>🙀</emoji>",
                    "<emoji document_id=5348312457750260828>🙀</emoji>"
                ]
            )

            try:
                count_float = float(count)
                form = (
                    "{} <b><i>{} {} is:</i></b>\n\n<emoji"
                    " document_id=6323374027985389586>🇺🇸</emoji>"
                    " <b>{}$</b>\n<emoji"
                    " document_id=6323289850921354919>🇺🇦</emoji>"
                    " <b>{}₴</b>\n<emoji"
                    " document_id=6323602387101550101>🇵🇱</emoji>"
                    " <b>{}zł.</b>\n<emoji"
                    " document_id=6323139226418284334>🇷🇺</emoji>"
                    " <b>{}₽</b>\n<emoji"
                    " document_id=6323135275048371614>🇰🇿</emoji>"
                    " <b>{}₸</b>\n<emoji"
                    " document_id=5215590800003451651>🪙</emoji> <b>{}"
                    " BTC</b>\n<emoji document_id=5217867240044512715>🪙</emoji>"
                    " <b>{} ETH</b>\n<emoji"
                    " document_id=5215276644620586569>🪙</emoji> <b>{} TON</b>"
                ).format(
                    smiles,
                    count_float,
                    coin,
                    round(api.get("USD", 0) * count_float, 2),
                    round(api.get("UAH", 0) * count_float, 2),
                    round(api.get("PLN", 0) * count_float, 2),
                    round(api.get("RUB", 0) * count_float, 2),
                    round(api.get("KZT", 0) * count_float, 2),
                    round(api.get("BTC", 0) * count_float, 4),
                    round(api.get("ETH", 0) * count_float, 4),
                    round(api.get("TON", 0) * count_float, 4),
                )

                await self.client.edit_message(message.chat_id, self.message_id, form)
            except KeyError:
                await utils.answer(message, self.strings["keyerror"])
                break
            except ValueError:
                await utils.answer(message, self.strings["inc_args"])
                break

            await asyncio.sleep(30)  # Ожидание 30 секунд перед следующей итерацией

    async def cnstopcmd(self, message: Message):
        """Остановить обновления курса"""
        self.running = False
        if self.update_task:
            self.update_task.cancel()
            self.update_task = None
        await utils.answer(message, self.strings["stopped"])
