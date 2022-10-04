import json

import aiogram

with open('settings.json', 'r', 'utf-8') as f:
    settings = json.load(f)
    bot = aiogram.Bot(token=settings['TOKEN'])

dp = aiogram.Dispatcher(bot)
