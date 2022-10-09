import psycopg2

conn = psycopg2.connect('dbname=records user=postgres')

cur = conn.cursor()

cur.execute("""CREATE TABLE users(
    id integer PRIMARY KEY,
    username text,
    count integer);""")