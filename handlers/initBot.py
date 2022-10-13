import json

import aiogram

from aiogram.contrib.fsm_storage.memory import MemoryStorage

SETTINGS_PATH = 'settings\settings.json'
with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
    settings = json.load(f)
    bot = aiogram.Bot(token=settings['TOKEN'])

storage = MemoryStorage()
dp = aiogram.Dispatcher(bot, storage=storage)
