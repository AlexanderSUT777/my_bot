# Файл с командами для админа
import json

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

from handlers.start_handlers.imports import *


# Класс со состояниями
class TimetableForm(StatesGroup):
    day = State()
    time = State()
    time_answer = State()

def return_kb():
    button1 = KeyboardButton('Продолжаем')
    button2 = KeyboardButton('Перейдём к другому дню')
    button3 = KeyboardButton("Закончим")
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(button1, button2, button3)
    
    return kb

@dp.message_handler(commands=['create'])
async def start_create_timetable(message: aiogram.types.Message,
                                state: aiogram.dispatcher.FSMContext):
    '''Хэндлер начинает работу с созданием расписания'''

    # Достаём из файла настроек айди админа
    with open('settings\settings.json') as f:
        is_admin = False
        json_load = json.load(f)
        if json_load['ADMIN'] == str(message.from_user.id):
            is_admin = True

    # Если флаг True - всё ок. Если нет - ответа нет.
    if is_admin:
        
        warning_text = ('Здравствуй. Прежде чем начать составлять'
        ' расписание для клиентов, запомни простые правила:'
        '\n1. Не вписывай месяц больше 12-го.'
        '\n2. Не вписывай время суток больше 23:59.'
        '\n3. Делай всё адекватно.'
        '\n Да прибудет с тобою сила!')

        text = ('Напиши число, в которое готов принять клиентов.'
        ' Формат данных будет в виде число.месяц, то есть'
        ' 15.10 - 15 октября.')
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
    insert.repeat_save_time(date=date['date'])

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
    
    #  
    date = await state.get_data()
    if message.text == 'Продолжаем':
        await message.answer(f'Введи время для записи на день {date["date"]}')
        await TimetableForm.time.set()

    elif message.text == 'Перейдём к другому дню':
        pass
    elif message.text == 'Закончим':
        pass
    else:
        kb = return_kb()
        await message.answer('Выбери один из вариантов', reply_markup=kb)
        return
    # Ответ положительный? Состояние остаётся прежним
    # Ответ отрицательный? Состояние переходит к уведомлению 
    # о создании дня для записи клиента


