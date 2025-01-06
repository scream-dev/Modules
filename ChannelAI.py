from gigachat import GigaChat
import random
import asyncio
from datetime import datetime, timedelta
from .. import loader, utils


@loader.tds
class GigaChatMod(loader.Module):
    """Module for using GigaChat"""

    strings = {
        "name": "GigaChat Channel",
        "api_key_missing": "Please set the API key in the module configuration.",
        "query_missing": "Please enter a query after the command.",
        "response_error": "Failed to get a response from GigaChat.",
        "error_occurred": "An error occurred: {}",
        "daily_plan_created": "Weekly plan has been created.",
        "weekly_summary": "Weekly summary: {}\n",
        "formatted_post": "{}\n=\n",
        "command_help": {
            ".planning": "Создает план на неделю.",
            ".show_sc": "Показывает хранилище данных.",
            ".gen": "Генерирует посты за день с задержкой.",
        },
    }

    strings_ru = {
        "api_key_missing": "Пожалуйста, установите API ключ в конфигурации модуля.",
        "query_missing": "Пожалуйста, введите запрос после команды.",
        "response_error": "Не удалось получить ответ от GigaChat.",
        "error_occurred": "Произошла ошибка: {}",
        "daily_plan_created": "План на неделю создан.",
        "weekly_summary": "Итог за неделю: {}\n",
        "formatted_post": "{}\n=\n",
        "command_help": {
            ".planning": "Создает план на неделю.",
            ".show_sc": "Показывает хранилище данных.",
            ".gen": "Генерирует посты за день с задержкой.",
        },
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "GIGACHAT_API_KEY",
            None,
            "Введите ваш API ключ для GigaChat.",
            "TIMEZONE",
            "Europe/Moscow",
            "Часовой пояс для работы скрипта.",
            "USER_SCRIPT",
            "Введите скрипт человека.",
            "DATA_STORAGE",
            {},
            "CHANNEL_ID",
            None,
            "Введите ID канала, в котором будет вестись личный блог.",
        )
        self.loop = asyncio.get_event_loop()

    async def gencmd(self, message):
        """Генерирует посты для блога"""
        await self.generate_daily_posts(message, self.config["USER_SCRIPT"])

    async def generate_daily_posts(self, message, user_script):
        daily_plan = await self.get_weekly_plan(user_script)
        posts = await self.create_posts(daily_plan)

        for post in posts:
            await utils.answer(message, self.strings("formatted_post").format(post))
            await asyncio.sleep(900)  # 15 минут задержка

    async def get_weekly_plan(self, user_script):
        query = "придумай уникальный подробный план на неделю для ведения личного канала человека который живёт в российской квартире и занимается разработкой зарабатывая этим себе на жизнь, разработка на html, python и js, нет девушки и у него лето, имя не упоминать. планы на дни разделять переходом на следующую строку и введением там знака /"
        return await self.ask_gigachat(query)

    async def ask_gigachat(self, query):
        api_key = self.config["GIGACHAT_API_KEY"]
        if not api_key:
            raise ValueError(self.strings("api_key_missing"))

        async with GigaChat(credentials=api_key, scope="GIGACHAT_API_PERS", verify_ssl_certs=False) as giga:
            response = await giga.chat(query)
            return response.choices[0].message.content.strip()

    async def create_posts(self, daily_plan):
        plan_days = daily_plan.split('/')
        posts = []
        for day in plan_days:
            posts_count = random.randint(10, 15)
            post_query = f"составь посты для личного канала человека по плану, [план]"
            post_query = post_query.replace('[план]', day.strip())
            daily_posts = await self.ask_gigachat(post_query)
            daily_posts_split = daily_posts.split('=')
            for post in random.sample(daily_posts_split, min(len(daily_posts_split), posts_count)):
                posts.append(post.strip())
        return posts

    async def planningcmd(self, message):
        """Создает план на неделю"""
        await utils.answer(message, self.strings("daily_plan_created"))

    async def show_sc(self, message):
        """Показывает хранилище данных"""
        data_storage = self.config["DATA_STORAGE"]
        await utils.answer(message, str(data_storage))

    async def gen_cmd(self, message):
        """Генерирует посты за день"""
        await self.gencmd(message)

    async def schedule_posts(self, day_posts):
        """Проводит планирование постов по расписанию"""
        while True:
            now = datetime.now(tz=timedelta(hours=int(self.config["TIMEZONE"].split(':')[0])))
            if now.hour == 8 and now.minute == 0:
                await self.gencmd()
            if now.hour == 22 and now.minute == 0:
                await self.gencmd()
            await asyncio.sleep(60)  # Проверять каждую минуту

    @loader.command(ru_doc="Получить помощь по командам")
    async def helpcmd(self, message):
        """Показывает список доступных команд"""
        help_text = "\n".join(f"{cmd}: {desc}" for cmd, desc in self.strings("command_help").items())
        await utils.answer(message, help_text)
