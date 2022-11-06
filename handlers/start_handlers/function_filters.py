import json
import datetime

from handlers.start_handlers.imports import *

def filter_for_query_handler_delete(call_data) -> bool:
    '''
    Фильтр для query_handler. От его значения зависит вызов
    хэндлера

    - call_data - данные, которые хранит в себе инлайн-кнопка
    '''
    
    if call_data == None:
        return 0
    # Создаём экземпляр
    get_days = InsertIntoDatabase(message=None)
    # Здесь цикл в получаемом списке, выбирается второй элемент кортежа из списка
    days = get_days.get_record()

    # Флаг 
    flag = False
    for date in days:
        # Здесь получаем секунды для проверки
        # путем создания объекта типа datetime.time
        full_date = call_data.split()
        time_obj = date[1]
        day_obj = date[0]
        time = time_obj.strftime("%H:%M:%S")
        day = day_obj.strftime("%Y-%m-%d")
        # Если время из базы данных совпадает со временем, которое хранит кнопка
        # то возвращается True

        if time == full_date[0] and day == full_date[1]:
            flag = True
            return flag


def get_admin_id():
    '''
    Достаёт из конфига айди админа, которому будут присылаться уведомления
    '''

    with open('settings\settings.json') as f:
        file = json.load(f)
        admin_id = file['ADMIN']
        
        return admin_id

def filter_callback_no(callback_data):
    '''
    Получает необработанную строку. Возвращает True если статус = no
    '''
    full_string = callback_data.split()
    if full_string[0] == 'no':
        return True
    else:
        return False

def filter_callback_yes(callback_data):
    '''
    Получает необработанную строку. Возвращает True если статус = yes
    '''
    full_string = callback_data.split()
    if full_string[0] == 'yes':
        return True
    else:
        return False