import handlers


if __name__ == '__main__':
    handlers.aiogram.executor.start_polling(handlers.initBot.dp, skip_updates=True)