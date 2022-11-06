from handlers.start_handlers.imports import *
from handlers.start_handlers.get_info import Form, create_timetable_inline

# Стартовый хендлер. При команде /start здороваемся с пользователем.
# Хендлер реагирующий на /start
@dp.message_handler(commands=["start"])
async def start_message(message: aiogram.types.Message, state: aiogram.dispatcher.FSMContext):
    '''
    Стартовый хендлер. Регистрирует начало работы с пользователем.
    Сразу переходит в состояние получения информации.
    '''
    # Делаем экземпляр класса и достаём данные о пользователе
    insert = InsertIntoDatabase(message)
    result = insert.check_user()

    # Здесь стоит реализовать возможность смены имени, и в принципе самого текста
    text = (f'Привет. Здесь вы можете записаться к Исполнителю на услугу. ' 
    'Для этого отправьте сперва свои имя и фамилию, затем '
    'номер телефона. После вам будут выведены доступные дни для '
    'записи.')
    
    # Проверяем, зарегистрирован ли пользователь?
    if result:
        inline_keyboard = await create_timetable_inline(message, state=state)
        if inline_keyboard.inline_keyboard:
            text = (f'Снова здравствуй. Хочешь вновь записаться?'
            ' Вот тебе время, доступное для записи:')
            await message.answer(text, reply_markup=inline_keyboard)
            await Form.get_date_state.set()
        else:
            text = ('Здравствуй. Свободных дней для записи нет. Загляни позже.')
            await message.answer(text)
            return 0 

    else:
        text = (f'Привет. Здесь ты можешь записаться к Исполнителю на услугу. ' 
    'Для этого отправьте сперва свои имя и фамилию, затем '
    'номер телефона. После вам будут выведены доступные дни для '
    'записи.')        
        # Выводим сообщение
        await message.answer(text)
        await Form.get_information_state.set()