# Файл с командами для админа
from ast import Delete
from dis import show_code
import json

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from handlers.start_handlers.function_filters import filter_for_query_handler_delete as filter_for_delete
from handlers.start_handlers.imports import *
from settings.convert_date import convering_date


# Класс со состояниями
class TimetableForm(StatesGroup):
    """Состояния"""
    day = State()
    time = State()
    time_answer = State()

class InlineStates(StatesGroup):
    """Состояния для инлайн клавиатур"""
    delete = State()
    get_info = State()
    inline_buttons_tape = State()
    back = State()


def return_kb():
    """Создаёт клавиатуру"""
    button1 = KeyboardButton('Продолжаем')
    button2 = KeyboardButton('Перейдём к другому дню')
    button3 = KeyboardButton("Закончим")
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(button1, button2, button3)
    
    return kb

def is_admin(message: aiogram.types.Message) -> bool:
    '''
    Эта функция проверяет, является ли человек, требующий
    исполнить команду - админом. 

    - Возвращает True в случае если user_id 
    прописан в settings.json
    - Возвращает False в случае если user_id 
    не прописан в settings.json
    '''
    with open('settings\settings.json') as f:
        is_admin = False
        json_load = json.load(f)
        if json_load['ADMIN'] == str(message.from_user.id):
            is_admin = True
    return is_admin

@dp.message_handler(commands=['create'])
async def start_create_timetable(message: aiogram.types.Message,
                                state: aiogram.dispatcher.FSMContext):
    '''Хэндлер начинает работу с созданием расписания'''

    admin = is_admin(message=message)
    # Если флаг True - всё ок. Если нет - ответа нет.
    if admin:
        
        warning_text = ('Прежде чем начать составлять'
        ' расписание для клиентов, запомни простые правила:'
        '\n1. Делай всё адекватно.'
        '\n2. Если у тебя что-то не получилось, смотри пункт 1'
        '\n3. Если у тебя и правда не получается, репорт @legannyst'
        '\n Да прибудет с тобою сила!')

        text = ('Напиши число, в которое готов принять клиентов.'
        ' Формат данных будет в виде год.месяц.число, то есть'
        ' 2022.10.15 - 15 октября.')
        await message.answer(warning_text)
        await message.answer(text)
        await TimetableForm.day.set()
    else:
        return None

@dp.message_handler(state=TimetableForm.day)
async def save_day(message: aiogram.types.Message,
                state: aiogram.dispatcher.FSMContext):
    '''Хэндлер сохраняет даты'''

    await state.update_data(date=message.text)

    # Создаём экземпляр класса для доступа к методам записи в базу данных
    
    text = ('Отлично. Теперь ты переходишь к заполнению времени в назначенный день.'
    ' Для этого просто указывай время, в формате час:минуты, например'
    ' 12:30.')

    await message.answer(text)
    # Сохраняем состояние ожидания получения времени.
    await TimetableForm.time.set()

@dp.message_handler(state=TimetableForm.time)
async def save_time(message: aiogram.types.Message,
                    state: aiogram.dispatcher.FSMContext):
    '''Хэндлер сохраняет время, которое ему отправляет админ'''

    # Создаём экземпляр класса для записи
    insert = InsertIntoDatabase(message)
    # Получаем значение прошлого сообщения
    # Оно нужно для записи в таблицу
    date = await state.get_data()
    try:
        insert.repeat_save_time(date=date['date'])
    except Exception as error:
        await message.answer('Что-то пошло не так.')
        await message.answer('Давай сначала и нормально')

        print(f'{error} в save_time' )

    text = ('Время записано.'
    ' Итак, теперь у тебя три варианта развития событий:'
    '\n1 - продолжим записывать время на тот же день'
    '\n2 - перейдём к заполнению другого дня'
    '\n3 - сверимся, всё ли правильно и закончим с расписанием.')

    kb = return_kb()

    await message.answer(text, reply_markup=kb)
    await TimetableForm.time_answer.set()

@dp.message_handler(state=TimetableForm.time_answer)
async def get_answer(message: aiogram.types.Message,
                    state: aiogram.dispatcher.FSMContext):
    '''
    Получаем ответ от админа для понимания продолжаем заполнять время
    для дня или нет
    '''
    
    # получаем дату для использования в сообщении.   
    date = await state.get_data()
    
    # Действие при продолжении: просто возвращаемся на состояние назад
    if message.text == 'Продолжаем':
        await message.answer(f'Введи время для записи на день {date["date"]}', reply_markup=ReplyKeyboardRemove())
        await TimetableForm.time.set()
    
    # Переходим на два состояния назад, к сохранению даты (дня)
    elif message.text == 'Перейдём к другому дню':
        await message.answer('Введи новую дату.', reply_markup=ReplyKeyboardRemove())
        await TimetableForm.day.set()
        
    # Спрашиваем, верно ли составлено расписание и переходим далее
    elif message.text == 'Закончим':
        get_data = InsertIntoDatabase(message)
        dates = get_data.get_record()

        # Перебираем полученные значения, формируем инлайн кнопки.
        button_list = []
        for date in dates:
            # В text возвращается готовая строка
            text = convering_date(date[0], date[1])
            # Тут создаются объекты кнопок
            button = InlineKeyboardButton(f'{text}', callback_data=(f"{str(date[1])} {str(date[0])}"))
            button_list.append(button)
            await InlineStates.delete.set()
        # А тут объект клавиатуры с распаковкой кнопок
        inline_keyboard = InlineKeyboardMarkup(row_width=1).add(*button_list)

        # Конец цепочки действий
        text_for_timetable = ('Итак, вот твоё составленное расписание'
        ' на данный момент:')
        await message.answer(text_for_timetable, reply_markup=inline_keyboard)
        
        text_for_delete = ('Для того, чтобы удалить запись, '
        ' нажми на нужный тебе день. Для возврата в режим создания'
        ' расписания используй /create\n'
        'Для выхода из режима создания напиши /end')
        await message.answer(text_for_delete, reply_markup=ReplyKeyboardRemove())
        
        await InlineStates.delete.set()

    # Если пользователь не выбрал ни один вариант
    else:
        kb = return_kb()
        await message.answer('Выбери один из вариантов', reply_markup=kb)
        return

@dp.message_handler(commands=['end'], state=InlineStates.delete)
async def end_create(message: aiogram.types.Message,
                    state: aiogram.dispatcher.FSMContext):
    '''
    Этот хэндлер реагирует на команду /end в режиме создания расписания
    и только в конце его создания, когда пользователю предлагается
    нажать на соответствующую дню кнопку для его удаления
    '''
    await message.answer('Ты вышел из режима создания расписания.')
    await state.finish()

@dp.callback_query_handler(lambda c: filter_for_delete(c.data), state=InlineStates.delete)
async def info_day(callback_query: aiogram.types.CallbackQuery):
    '''
    Хэндлер реагирует на нажатие кнопки и удаляет
    выбранный день из списка
    '''
        # Удаляем запись из базы данных
    delete_record = InsertIntoDatabase(message=None)
    delete_record.delete_record(data=callback_query.data)
    # Даём ответ клиенту
    await bot.answer_callback_query(callback_query.id)
    # Оповещаем клиента об удалении
    await callback_query.answer(show_alert=True)