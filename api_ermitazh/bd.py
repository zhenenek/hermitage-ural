import sqlite3
from tonality import sentiment_value
def save_to_db(result):
    connection = sqlite3.connect('database_api.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        reason TEXT NOT NULL,
        health TEXT NOT NULL,
        tonality TEXT NOT NULL,
        age INTEGER
    )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS name ON Users (name)')

    name = result.split('Имя: ')[1].split(',')[0].strip()
    reason = result.split('Причина: ')[1].split(',')[0].strip()
    health = result.split('Удовлетворение: ')[1].split(',')[0].strip()
    tonality = sentiment_value
    age = result.split('Возраст: ')[1].split(',')[0].strip()

    cursor.execute('''
    INSERT INTO Users (name, reason, health, tonality, age)
    VALUES (?, ?, ?, ?, ?)
''', (name, reason, health, sentiment_value, age))

    connection.commit()
    connection.close()