import sqlite3
import json

def save_to_db(result, sentiment_data):
    try:
        connection = sqlite3.connect('database_api.db')
        cursor = connection.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            reason TEXT NOT NULL,
            satisfaction TEXT NOT NULL,
            age INTEGER,
            full_analysis TEXT NOT NULL
        )''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS name_index ON Users (name)')

        data = {
            'name': extract_value(result, 'Имя:'),
            'reason': extract_value(result, 'Причина:'),
            'satisfaction': extract_value(result, 'Удовлетворение:'),
            'age': extract_value(result, 'Возраст:'),
            'full_analysis': json.dumps(sentiment_data['full_analysis'])
        }

        cursor.execute('''
        INSERT INTO Users (name, reason, satisfaction, age, full_analysis)
        VALUES (?, ?, ?, ?, ?)''', 
        (
            data['name'], 
            data['reason'], 
            data['satisfaction'],
            data['age'],
            data['full_analysis']
        ))

        connection.commit()
        print(f"Сохранено: {data['name']}")
        print(f"Анализ тональности: {data['full_analysis']}")
        
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")
    finally:
        if connection:
            connection.close()

def extract_value(text, key):
    try:
        return text.split(key)[1].split(',')[0].strip()
    except:
        return "Не указано"