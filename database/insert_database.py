# Здесь располагается класс для записи в базу данных значений из получаемого аргумента message.
import datetime

import aiogram
import psycopg2


class InsertIntoDatabase():
    def __init__(self, message: aiogram.types.Message) -> None:
        '''Инициализируем экземпляры класса и атрибуты'''
        self.message = message
        self.conn = psycopg2.connect('dbname=records user=postgres')

    def save_username_user(self) -> None:
        '''
        Сохраняем имя-фамилию в базу данных, 
        а также сохраняем username телеграма
        '''
        cur = self.conn.cursor()

        cur.execute(f'''INSERT INTO 
        users(user_id, username, lastfirstname)
        VALUES(%s, %s, %s);
        ''', (self.message.from_user.id, self.message.from_user.username, self.message.text))

        self.conn.commit()
        print('Данные сохранены')

    def save_phone_number(self) -> None:
        '''
        Сохраняем номер телефона клиента в базу данных
        '''
        cur = self.conn.cursor()

        cur.execute(f'''UPDATE users
        SET phone_number = %s
        WHERE user_id = %s;''', (self.message.text, self.message.from_user.id))

        self.conn.commit()
        print('Данные сохранены')
    
    def check_user(self):
        '''Достаём user_id из таблицы users'''

        cur = self.conn.cursor()
        cur.execute('''SELECT * FROM users WHERE user_id = %s;''', (self.message.from_user.id,))
        print('Данные получены')
        return cur.fetchall()
        
    def save_number_date(self):
        '''Сохраняем дату в таблицу'''

        cur = self.conn.cursor()
        cur.execute('''INSERT INTO timetable(day)
        VALUES(%s);''', (self.message.text,))

        self.conn.commit()
        print('Данные сохранены')

    def repeat_save_time(self, date):
        '''Метод для повторного сохранения дня и времени'''
        cur = self.conn.cursor()
        cur.execute('''INSERT INTO timetable(day, time)
        VALUES(%s, %s);''', (date, self.message.text))

        self.conn.commit()
        print('Данные сохранены')
    
    def get_record(self):
        '''Метод для получения всех дат записей в текущий сеанс'''
        cur = self.conn.cursor()
        cur.execute('''SELECT day, time FROM timetable''')
        result = cur.fetchall()

        print('Данные получены')
        return result
    
    def get_record_for_client(self):
        '''Метод для предоставления клиенту свободных дней записи'''
        cur = self.conn.cursor()
        cur.execute('''SELECT day, time, status FROM timetable''')
        print('Данные получены')
        result = cur.fetchall()
        return result
    
    def delete_record(self, data):
        '''Удаляет запись из таблицы timetable'''
        cur = self.conn.cursor()
        data_full = data.split()

        # Получаем отдельно объект времени и дня
        time = datetime.datetime.strptime(data_full[0], "%H:%M:%S").time()
        day = datetime.datetime.strptime(data_full[1], "%Y-%m-%d").date()

        # Удаляем
        cur.execute('''DELETE FROM timetable
        WHERE time = %s AND day = %s''', (time, day))

        # Сохраняем
        self.conn.commit()
        print('Данные удалены')
    
    def get_info_timetable(self, date):
        '''Получает всю информацию из таблицы timetable'''
        cur = self.conn.cursor()
        data_full = date.split()

        # Получаем объекты времени и дня
        time = datetime.datetime.strptime(data_full[0], "%H:%M:%S").time()
        day = datetime.datetime.strptime(data_full[1], "%Y-%m-%d").date()

        # Формируем запрос
        cur.execute("""SELECT * FROM timetable
        WHERE time = %s AND day = %s""", (time, day))
        result = cur.fetchall()
        return result

    def get_phone_number(self, user_id):
        '''Возвращает номер телефона через user_id'''

        cur = self.conn.cursor()
        cur.execute('''SELECT phone_number
        FROM users WHERE user_id = %s''', (user_id,))
        print('Данные получены')
        result = cur.fetchall()
        return result
    
    def get_name_user(self, user_id):
        '''Возвращает ФИО юзера'''

        cur = self.conn.cursor()
        cur.execute('''SELECT lastfirstname
        FROM users WHERE user_id = %s''', (user_id,))

        result = cur.fetchall()
        return result
    
    def save_active_status(self, date, user_id):
        """Изменяет статус записи"""
        cur = self.conn.cursor()
        data_full = date.split()
        # Получаем объекты времени и дня
        time = datetime.datetime.strptime(data_full[0], "%H:%M:%S").time()
        day = datetime.datetime.strptime(data_full[1], "%Y-%m-%d").date()

        cur.execute('''UPDATE timetable 
        SET status = %s, user_id = %s
        WHERE time = %s and day = %s''', ('Занято', user_id, time, day))
        print('Данные изменены')
        self.conn.commit()

    def get_full_record(self):
        """
        Метод достает все значения для формирования только свободных записей
        для создания инлайн кнопок
        """
        cur = self.conn.cursor()
        cur.execute('''SELECT * FROM timetable''')

        result = cur.fetchall()
        return result
    
    def get_name_and_phone_number(self, user_id):
        '''
        Достаём из базы данных имя и номер мобильного телефона
        '''
        cur = self.conn.cursor()
        cur.execute('''SELECT lastfirstname, phone_number
        FROM users
        WHERE user_id = %s''', (user_id,))

        result = cur.fetchall()
        return result
    
    def update_status_none(self, date):
        '''
        Данный метод удаляет статус у записи
        '''
        cur = self.conn.cursor()
        data_full = date.split()
        # Получаем объекты времени и дня
        time = datetime.datetime.strptime(data_full[0], "%H:%M:%S").time()
        day = datetime.datetime.strptime(data_full[1], "%Y-%m-%d").date()

        cur.execute('''UPDATE timetable
        SET status = %s, user_id = %s
        WHERE day = %s and time = %s''', (None, None, day, time))
        print('Статус изменён')
        self.conn.commit()