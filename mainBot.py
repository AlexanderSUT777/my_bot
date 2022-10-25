import aiogram

import handlers
import handlers.initBot

if __name__ == '__main__':
    aiogram.executor.start_polling(handlers.initBot.dp, skip_updates=True)
    