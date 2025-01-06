import datetime
import logging
import time
from telethon.tl.types import Message
from .. import loader, utils

logger = logging.getLogger(__name__)

class PlanManager(loader.Module):
    strings = {
        "name": "PlanManager",
        "plans_empty": "Список планов пуст.",
        "plans_list": "Список планов:\n{}",
        "plan_added": "План добавлен: {}",
        "plan_deleted": "План удалён: {}",
        "plan_crossed": "План вычеркнут: {}",
        "plan_does_not_exist": "План не найден: {}",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "timezone",
                "0",
                lambda: "Используйте 1, -1, -3 и т. д. для установки смещения времени.",
            ),
        )
        self.plans = []  # Хранилище планов
        self.start_cleanup()

    def start_cleanup(self):
        """Запускает процесс очистки планов"""
        time_interval = 60  # Проверка каждый 60 секунд
        while True:
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=int(self.config["timezone"]))))
            if now.hour == 0 and now.minute == 0:  # В полночь
                self.plans.clear()  # Очистка планов
                logger.info("Список планов очищен.")
            time.sleep(time_interval)

    @loader.command(command="makeplan")
    async def makeplan(self, message: Message):
        """Добавляет новый план"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "Вы должны указать план.")
            return
        
        self.plans.append(args)
        await utils.answer(message, self.strings["plan_added"].format(args))

    @loader.command(command="plan")
    async def show_plans(self, message: Message):
        """Показывает список планов"""
        if not self.plans:
            await utils.answer(message, self.strings["plans_empty"])
            return
        
        formatted_plans = "\n".join(f"{i + 1}. {plan}" for i, plan in enumerate(self.plans))
        await utils.answer(message, self.strings["plans_list"].format(formatted_plans))

    @loader.command(command="plan_yes")
    async def cross_plan(self, message: Message):
        """Вычеркивает план из списка"""
        args = utils.get_args_raw(message)
        if not args.isdigit() or int(args) < 1 or int(args) > len(self.plans):
            await utils.answer(message, "Неверный номер плана.")
            return
        
        index = int(args) - 1
        crossed_plan = f"~~{self.plans[index]}~~"
        self.plans[index] = crossed_plan
        await utils.answer(message, self.strings["plan_crossed"].format(crossed_plan))

    @loader.command(command="delplan")
    async def del_plan(self, message: Message):
        """Удаляет план из списка"""
        args = utils.get_args_raw(message)
        if not args.isdigit() or int(args) < 1 or int(args) > len(self.plans):
            await utils.answer(message, "Неверный номер плана.")
            return

        index = int(args) - 1
        deleted_plan = self.plans.pop(index)
        await utils.answer(message, self.strings["plan_deleted"].format(deleted_plan))
