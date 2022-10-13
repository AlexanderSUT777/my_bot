from aiogram.dispatcher.filters.state import StatesGroup, State

from handlers.start_handlers.imports import *

# Создаём класс для FSM
class Form(StatesGroup):
    get_number_state = State() # Для получения мобильного номера
    get_information_state = State() # для получения имени-фамилии
    get_date_state = State() # для получения даты записи.

# Тут мы получаем номер клиента
@dp.message_handler(state=Form.get_information_state)
async def get_information_user(message: aiogram.types.Message,
                            state: aiogram.dispatcher.FSMContext):
    '''Хендлер, который сохраняет имя-фамилию клиента.'''

    # Текст сообщения
    text = ('Имя записали. Дальше - номер мобильного телефона. Напишите '
            'его следующим сообщением, в формате +7:')
    # Вот в этой строчке мы в переменную состояния сохраняем информацию
    # о пользователе:
    await state.update_data(information_user=message.text)

    # Выводим сообщение и переходим к следующему состоянию.
    await message.answer(text)
    await Form.get_number_state.set()

    # Попытка сохранить данные
    insert_in_db = InsertIntoDatabase(message)
    insert_in_db.save_username_user()

@dp.message_handler(state=Form.get_number_state)
async def get_phone_number(message: aiogram.types.Message,
                        state: aiogram.dispatcher.FSMContext):
    '''Хэндлер, который сохраняет номер телефона клиента'''

    # текст сообщения
    text = ('Номер мобильного телефона сохранён. По нему с вами свяжется'
            ' мастер. Далее - выберите дату, на которую у мастера'
            ' есть свободное место')
    
    # Сохраняем в переменную состояния мобильный телефон
    await state.update_data(phone_number=message.text)

    # Выводим сообщение и переходим к финалу
    await message.answer(text)
    await Form.get_date_state.set() 

    # Сохраняем номер телефона
    insert_in_db = InsertIntoDatabase(message)
    insert_in_db.save_phone_number()


@dp.message_handler(state=Form.get_date_state)
async def change_date(message: aiogram.types.Message,
                    state: aiogram.dispatcher.FSMContext):
    '''Хэндлер записывает дату записи клиента.'''
    
    # Здесь тесное взаимодействие с базой данных, так что этот этап - на потом.
    # Номер телефона служит уникальным идентификатором
    # Нужно сохранить через переменную состояния номер телефона и имя-фамилию.
    #  А так же одну из предложенных дат.