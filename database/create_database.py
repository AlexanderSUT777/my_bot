import psycopg2

conn = psycopg2.connect('dbname=records user=postgres')
cur = conn.cursor()

def create_users_table():
    '''
    Создаёт таблицу для юзеров
    '''

    cur.execute("""CREATE TABLE users(
        user_id bigint PRIMARY KEY,
        username text NOT NULL,
        lastfirstname text NOT NULL,
        phone_number char(16));""") 
    conn.commit()
    print('Таблица users создана')


def create_timetable():
    '''Создаёт таблицу для расписания'''

    cur.execute('''CREATE TABLE timetable(
        user_id bigint,
        day date,
        time time,
        status text,
        FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE);''')
    
    conn.commit()
    print('Таблица timetable создана')

text = ('Введите число, соответствующее создаваемой таблице'
' где:\n1 - users\n2 - timetable:\n')
choose = int(input(text))
if choose == 1:
    create_users_table()
elif choose == 2:
    create_timetable()
else:
    print('Только из предложенных!')
