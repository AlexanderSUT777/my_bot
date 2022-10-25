import datetime
from distutils.command.build_scripts import first_line_re

from handlers.start_handlers.imports import *

def filter_for_query_handler_delete(call_data) -> bool:
    '''
    Фильтр для query_handler. От его значения зависит вызов
    хэндлера

    - call_data - данные, которые хранит в себе инлайн-кнопка
    '''
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
