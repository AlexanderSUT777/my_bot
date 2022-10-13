# Здесь располагается класс для записи в базу данных значений из получаемого аргумента message.

import psycopg2


class InsertIntoDatabase():
    def __init__(self, message) -> None:
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
    
    def save_time(self, date):
        '''Сохраняем время в таблицу''' 

        cur = self.conn.cursor()
        cur.execute('''UPDATE timetable 
        SET time = %s
        WHERE day = %s;''', (self.message.text, date))

        self.conn.commit()
        print('Данные сохранены')

    def repeat_save_time(self, date):
        '''Метод для повторного сохранения дня и времени'''
        cur = self.conn.cursor()
        cur.execute('''INSERT INTO timetable(day, time)
        VALUES(%s, %s);''', (date, self.message.text))

        self.conn.commit()
        print('Данные сохранены')