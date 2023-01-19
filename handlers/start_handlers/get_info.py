import datetime

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from handlers.start_handlers.imports import *
from settings.convert_date import convering_date
from handlers.start_handlers.function_filters import filter_for_query_handler_delete, get_admin_id, filter_callback_no
from handlers.start_handlers.function_filters import filter_callback_yes


# Создаём класс для FSM
class Form(StatesGroup):
    get_number_state = State() # Для получения мобильного номера
    get_information_state = State() # для получения имени-фамилии
    get_date_state = State() # для получения даты записи.
    get_answer = State() # Для получения ответа Исполнителя

async def create_timetable_inline(message, state: aiogram.dispatcher.FSMContext):
    text_for_none = 'Нет времени доступного для записи. Обратитесь позже'
    
    # Получаем даты
    get_data = InsertIntoDatabase(message)
    dates = get_data.get_full_record()
    if dates == None:
        await message.answer(text_for_none)
        return None
    # Перебираем полученные значения, формируем инлайн кнопки.
    button_list = []
    for date in dates:
        if 'Занято' not in date:
            # В text возвращается готовая строка
            text = convering_date(date=date[1], time=date[2])
            # Тут создаются объекты кнопок
            button = InlineKeyboardButton(f'{text}', callback_data=(f"{str(date[2])} {str(date[1])}"))
            button_list.append(button)

            await state.update_data(date=f"{str(date[2])} {str(date[1])}")
            await Form.get_date_state.set()
    # А тут объект клавиатуры с распаковкой кнопок
    inline_keyboard = InlineKeyboardMarkup(row_width=1).add(*button_list)
    return inline_keyboard  

# Тут мы получаем номер клиента
@dp.message_handler(state=Form.get_information_state)
async def get_information_user(message: aiogram.types.Message,
                            state: aiogram.dispatcher.FSMContext):
    '''Хендлер, который сохраняет имя-фамилию клиента.'''
    if message.text == '/end':
        await state.finish()
        await message.answer('Вы прервали процедуру регистрации. Для возврата к регистрации напишите /start')
        return 0
    # Текст сообщения
    text = ('Имя записали. Дальше - номер мобильного телефона. Напишите '
            'его следующим сообщением, в формате +7')
    # Вот в этой строчке мы в переменную состояния сохраняем информацию
    # о пользователе:
    await state.update_data(name_user=message.text)

    # Выводим сообщение и переходим к следующему состоянию.
    await message.answer(text)
    await Form.get_number_state.set()

    # Попытка сохранить данные
    # insert_in_db = InsertIntoDatabase(message)
    # insert_in_db.save_username_user()

@dp.message_handler(state=Form.get_number_state)
async def get_phone_number(message: aiogram.types.Message,
                        state: aiogram.dispatcher.FSMContext):
    '''Хэндлер, который сохраняет номер телефона клиента'''
    if message.text == '/end':
        await state.finish()
        await message.answer('Вы прервали процедуру регистрации. Для возврата к регистрации напишите /start')
        return 0
    # текст сообщения
    text_message = ('Номер мобильного телефона сохранён. По нему с вами свяжется'
            ' Исполнитель. Далее - выберите дату, на которую у Исполнитель'
            ' есть свободное место')
    
    inline_keyboard = await create_timetable_inline(message=None, state=state) 
    data_state = await state.get_data()
    # Выводим сообщение и переходим к финалу
    # await state.update_data(phone_number=message.text)
    InsertIntoDatabase(message).save_phone_number(name=data_state['name_user']) 
    await message.answer(text_message, reply_markup=inline_keyboard)
    await Form.get_date_state.set() 

    # Сохраняем информацию о пользователе
    
@dp.callback_query_handler(state=Form.get_date_state)
async def save_user_date(callback_query: aiogram.types.CallbackQuery,
    state: aiogram.dispatcher.FSMContext):
    """
    Хэндлер реагирует на нажатие кнопки, когда клиенту
    предложено выбрать свободный день для записи.
    Нажатие на день сохраняет его в базе данных с пометкой "занято".
    """
    InsertIntoDatabase(message=None).save_active_status(date=callback_query.data,
             user_id=callback_query.from_user.id)
    await callback_query.answer('Исполнителю отправлено уведомление. Ожидайте '
    ' ответа от Исполнителя.', show_alert=True)
    
    admin_id = get_admin_id()
    # Текст, который будет отправлен админу и кнопки
    name_and_number = InsertIntoDatabase(message=None).get_name_and_phone_number(
                user_id=callback_query.from_user.id)

    date = callback_query.data
    date = date.split()
    time = datetime.datetime.strptime(date[0], "%H:%M:%S").time()
    day = datetime.datetime.strptime(date[1], "%Y-%m-%d").date()

    date_text = convering_date(date=day, time=time)

    text = (f'У вас новая заявка на {date_text}.\nЭто {name_and_number[0][0]}.\nНомер телефона: {name_and_number[0][1]}'
    f'\nТелеграм: @{name_and_number[0][2]}')
    # Создаём две инлайн кнопки для принятия или отмены заявки:
    button_list = []

    button_yes = InlineKeyboardButton('Принять заявку', callback_data=f'yes {callback_query.from_user.id} {callback_query.data}')
    button_no = InlineKeyboardButton('Отменить заявку', callback_data=f'no {callback_query.from_user.id} {callback_query.data}')
    button_list.append(button_yes)
    button_list.append(button_no)
    inline_keyboard = InlineKeyboardMarkup(row_width=3).add(*button_list)

    # operative_storage[f'{callback_query.from_user.id}'] = callback_query.data
    # waiting_users.append(callback_query.from_user.id)

    await bot.send_message(chat_id=admin_id, text=text, reply_markup=inline_keyboard)
    await state.finish()

@dp.callback_query_handler(lambda c: filter_callback_no(c.data))
async def delete_user_from_record(callback_query: aiogram.types.CallbackQuery):
    '''
    Колбэк реагирует на нажатие Исполнителем кнопки "Отменить заявку". Меняет статус заявки.
    '''
    string = callback_query.data.split()
    await callback_query.message.edit_text('Заявка отклонена.', reply_markup=None)
    user_id = InsertIntoDatabase(message=callback_query.message).get_info_timetable(date=f'{string[2]} {string[3]}')
    InsertIntoDatabase(message=None).update_status_none(date=f'{string[2]} {string[3]}')
    
    await bot.send_message(chat_id=user_id[0][0], text='Ваша заявка отклонена.')
    

@dp.callback_query_handler(lambda c: filter_callback_yes(c.data))
async def invite_user(callback_query: aiogram.types.CallbackQuery):
    """
    Колбэк реагирует на нажатие Исполнителем кнопки "Принять заявку". Заявка не изменяется.
    Клиенту приходит сообщение, мастеру приходит уведомление о том что он принял заявку
    """
    string = callback_query.data.split()
    # Получаем user_id для отправки потом ему сообщения. Переменная содержит в себе кортеж со списками
    user_id = InsertIntoDatabase(message=callback_query.message).get_info_timetable(date=f'{string[2]} {string[3]}')
    # Ответ пользователю
    await callback_query.message.edit_text('Заявка принята', reply_markup=None)
    await bot.send_message(chat_id=user_id[0][0], text='Ваша заявка принята')
    await bot.answer_callback_query(callback_query.id)

@dp.message_handler(commands=['end'], state=Form.get_date_state)
@dp.message_handler(commands=['end'], state=Form.get_information_state)
@dp.message_handler(commands=['end'], state=Form.get_number_state)
async def reset_state(message: aiogram.types.Message, state: aiogram.dispatcher.FSMContext):
    '''При подаче заявки на запись может позволить прекратить заполнение заявки'''
    await state.finish()
    await message.answer('Вы прервали регистрацию. Воспользуйтесь /start для возобновления этой процедуры.')