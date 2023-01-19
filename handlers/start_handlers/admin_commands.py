from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from handlers.start_handlers.function_filters import filter_for_query_handler_delete as filter_for_delete

from handlers.initBot import bot
from settings.convert_date import convering_date
from handlers.start_handlers.imports import *
from handlers.start_handlers.create_timetable import is_admin, InlineStates


@dp.message_handler(commands=['timetable'])
async def show_timetable(message: aiogram.types.Message):
    '''
    Хэндлер реагирует на команду /timetable. Выводит инлайн кнопки
    которые содержат в своем имени дату созданного расписания.
    От сюда начинается цепочка событий для редактирования и просмотра 
    информации о любом дне в расписании.
    '''
    admin = is_admin(message)

    if admin:
        get_data = InsertIntoDatabase(message)
        dates = get_data.get_record()
        if dates:
            # Перебираем полученные значения, формируем инлайн кнопки.
            button_list = []
            for date in dates:
                # В text возвращается готовая строка
                text = convering_date(date[0], date[1])
                # Тут создаются объекты кнопок
                button = InlineKeyboardButton(f'{text}', callback_data=(f"{str(date[1])} {str(date[0])}"))
                button_list.append(button)
            # А тут объект клавиатуры с распаковкой кнопок
            inline_keyboard = InlineKeyboardMarkup(row_width=1).add(*button_list)
    
            # Конец цепочки действий
            # Вывод сообщений
            text_pre_inline = ('Итак, вот твоё составленное расписание. Нажми на интересующую тебя дату для перехода '
            'в режим настройки.')
            await message.answer(text_pre_inline, reply_markup=inline_keyboard)
            text_for_warning = ('Для выхода из режима просмотра расписания введи /end')
            await message.answer(text_for_warning, reply_markup=ReplyKeyboardRemove())
        
            await InlineStates.get_info.set()
        else:
            text = ('На данный момент расписание не составлено.'
            ' Используй команду /create для его создания.')
            await message.answer(text)
            return

@dp.callback_query_handler(state=InlineStates.get_info)
async def get_info_inline(callback_query: aiogram.types.CallbackQuery):
    '''
    Этот хэндлер реагирует на нажатие любого дня
    из списка инлайн кнопок. Он редактирует клавиатуру, предоставляя
    пользователю 4 кнопки для дальнейшего действия. Из них работают только 3
    Кнопки "Удалить", "Назад" и кнопка с номером телефона пользователя.
    Само сообщение прикрепленное к кнопке меняется на ФИО человека.
    При нажатии на кнопку удалить - запись отменяется, человеку приходит 
    уведомление в личные сообщения. Если никто не записан - никому ничего
    не приходит.
    '''
    # Получаем данные из базы данных в виде списка кортежей
    infos = InsertIntoDatabase(message=None).get_info_timetable(date=callback_query.data)
    # Создаём список, используемый для создания инлайн клавиатуры
    button_list = []
    # Формируются инлайн кнопки. Тут же добавляются в список.
    for info in infos:
        # Кнопка с информацией о дне
        text = convering_date(date=info[1], time=info[2])
        button_info = InlineKeyboardButton(f'{text}', callback_data='info')
        # Получение номера мобильного телефона
        phone_number_db = InsertIntoDatabase(message=None).get_phone_number(user_id=info[0])
        for num in phone_number_db:
            phone_number = num[0]

        # Кнопка с информацией о том, кто записан
        if info[0] == None and info[3] == None:
            button = InlineKeyboardButton(f'Никто не записан - свободно', callback_data='None')
        elif info[0] != None or info[3] != None:
            # Имя записанного
            name_db = InsertIntoDatabase(message=None).get_name_user(user_id=info[0])
            for name_list in name_db:
                name = name_list[0]    
            await callback_query.message.edit_text(f'{name}')
            button = InlineKeyboardButton(f'Запись на день - {phone_number}', callback_data=phone_number)
        # Кнопка "Назад"
        button_back = InlineKeyboardButton('Назад', callback_data='back')
        # Кнопка "Удалить"
        button_delete = InlineKeyboardButton('Удалить', callback_data=f'{str(info[2])} {str(info[1])} ')
        # Добавление в список кнопок
        button_list.append(button_info)
        button_list.append(button)
        button_list.append(button_back)
        button_list.append(button_delete)

    # Создаётся инлайн клавиатура
    inline_keyboard = InlineKeyboardMarkup(row_width=1).add(*button_list)    
    # Ответ клиенту
    await bot.answer_callback_query(callback_query.id)
    # Редактирование прошлой клавиатуры
    await callback_query.message.edit_reply_markup(reply_markup=inline_keyboard)
    await InlineStates.inline_buttons_tape.set()
    

@dp.callback_query_handler(lambda c: c.data == "back", state=InlineStates.inline_buttons_tape)
async def back_inline(callback_query: aiogram.types.CallbackQuery, state: aiogram.dispatcher.FSMContext):
    """
    Реагирует на нажатие кнопки "Назад" в состоянии просмотра информации
    о записи.

    - callback_query - содержит всю информацию от API Telegram
    - state - хранит промежуточную информацию
    """
    # Тут мы получаем все записи на указанные админом дни. 
    get_data = InsertIntoDatabase(callback_query.message).get_record()
    # В цикле формируется список кнопок, на основе полученного списка кортежей
    button_list = []
    if get_data:
        for date in get_data:
            # date - кортеж с двумя значениями. date[0] - время
            # date[1] - день
            # state - хранит в себе кортеж
            
            await state.update_data(date=None)
            text_date = convering_date(date[0], date[1])
            button = InlineKeyboardButton(f'{text_date}', callback_data=(f"{str(date[1])} {str(date[0])}"))
            button_list.append(button)
        # А тут объект клавиатуры с распаковкой кнопок
        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(*button_list)
        # Даём ответ клиенту и изменяем клавиатуру под сообщением, возвращаемся в состояние
        # ожидания выбора дня для получения информации
        text_pre_inline = ('Итак, вот твоё составленное расписание. Нажми на интересующую тебя дату для перехода '
        'в режим настройки.')
        await callback_query.message.edit_text(text_pre_inline)
        await callback_query.message.edit_reply_markup(reply_markup=inline_keyboard)
        await bot.answer_callback_query(callback_query.id)
        await InlineStates.get_info.set()
    else:
        text = ('У вас больше нет дней в расписании. Для перехода в режим'
        ' создания используй /create')
        await callback_query.message.edit_text(text)
        await state.finish()

@dp.callback_query_handler(lambda c: filter_for_delete(c.data), state=InlineStates.inline_buttons_tape)
async def delete_record_in_timetable(callback_query: aiogram.types.CallbackQuery):
    '''
    Хэндлер реагиуерт на нажатие кнопки "Удалить" в состоянии просмотра
    информации о записи. Запись удаляется из базы данных.
    Если человек был записан, ему приходит уведомление.

    - callback_query - содержит всю информацию от API Telegram
    '''
    # Получаем дату от кнопки
    get_data = callback_query.data
    # Удаляем записи, отвечаем пользователю
    InsertIntoDatabase(message=None).delete_record(get_data)
    await callback_query.answer('Удалено')
    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(commands=['end'], state=InlineStates.inline_buttons_tape)
@dp.message_handler(commands=['end'], state=InlineStates.get_info)
@dp.message_handler(commands=['end'], state=InlineStates.back)
@dp.message_handler(commands=['end'], state=InlineStates.delete)
async def escape_from_looking_timetable(message: aiogram.types.Message,
state: aiogram.dispatcher.FSMContext):
    '''
    Хэндлер реагирует на команду end. Досрочно закрывает все состояния.
    '''
    await message.answer('Ты вышел из режима')
    await state.finish()