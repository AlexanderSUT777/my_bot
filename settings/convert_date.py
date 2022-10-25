import datetime

def convering_date(date, time):
    '''Конвертируем дату в человеческий вид'''
    months = {
        'Январь': 'January',
        "Февраль": "February",
        "Март": "March",
        'Апрель': "April",
        "Май": "May",
        "Июнь": "June",
        "Июль": "July",
        "Август": "August",
        "Сентябрь": "September",
        "Октябрь": "October",
        "Ноябрь": "November"
    } 

    # Меняем с английского, на русский
    dt_month = date.strftime("%B")
    for rus_month, eng_month in months.items():
        if dt_month == eng_month:
            dt_month = rus_month

    # Конечный результат
    dt_string = date.strftime(f"\nДата - {dt_month} %d,")
    dt_string_time = time.strftime("\nвремя - %H:%M")

    # Соединяем в одну строку
    dt_string += dt_string_time
    
    return dt_string
