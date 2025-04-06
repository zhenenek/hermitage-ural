import sqlite3
import json
import logging

logger = logging.getLogger(__name__)

def save_to_db(result, sentiment_data, call_id):
    
    connection = None
    try:
        connection = sqlite3.connect('database_api.db')
        cursor = connection.cursor()
        
        
        logger.debug(f"Данные для сохранения (call_id={call_id}):")
        logger.debug(f"Result: {result}")
        logger.debug(f"Sentiment: {json.dumps(sentiment_data, indent=2)}")
        
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                operator TEXT NOT NULL,
                reason TEXT NOT NULL,
                satisfaction TEXT NOT NULL,
                age INTEGER,
                full_analysis TEXT NOT NULL
            )
        ''')
        
        
        data = {
            'call_id': call_id,
            'name': extract_value(result, 'Имя:'),
            'operator': extract_value(result, 'Оператор:'),
            'reason': extract_value(result, 'Причина:'),
            'satisfaction': extract_value(result, 'Удовлетворение:'),
            'age': extract_value(result, 'Возраст:'),
            'full_analysis': json.dumps(sentiment_data['full_analysis'])
        }
        
        
        logger.debug(f"Извлеченные данные: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        
        required_fields = ['call_id', 'name', 'operator', 'reason', 'satisfaction']
        for field in required_fields:
            if not data.get(field):
                logger.error(f"Отсутствует обязательное поле {field}")
                raise ValueError(f"Missing required field: {field}")

        
        cursor.execute('''
            INSERT INTO Users 
            (call_id, name, operator, reason, satisfaction, age, full_analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['call_id'],
            data['name'], 
            data['operator'],
            data['reason'], 
            data['satisfaction'],
            data['age'],
            data['full_analysis']
        ))
        
        connection.commit()
        logger.info(f"Успешно сохранено для call_id={call_id}")
        
        
        cursor.execute("SELECT * FROM Users WHERE call_id = ?", (call_id,))
        record = cursor.fetchone()
        if record:
            logger.debug(f"Проверка записи: {record}")
        else:
            logger.error("Запись не найдена после вставки")
            
    except Exception as e:
        logger.error(f"Ошибка сохранения (call_id={call_id}): {str(e)}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()

def extract_value(text, key):
    """Улучшенный парсер ответов нейросети"""
    try:
       
        start_idx = text.find(key)
        if start_idx == -1:
            return "Не указано"
        
        
        start_idx += len(key)
        
        
        end_idx = len(text)
        for marker in ['\n', 'Имя:', 'Оператор:', 'Причина:', 'Удовлетворение:', 'Возраст:']:
            if marker == key:  
                continue
            marker_pos = text.find(marker, start_idx)
            if marker_pos != -1 and marker_pos < end_idx:
                end_idx = marker_pos
        
        
        value = text[start_idx:end_idx].strip()
        
        
        value = value.rstrip(',').strip()
        
        return value if value else "Не указано"
    except Exception as e:
        logging.error(f"Ошибка парсинга '{key}': {str(e)}")
        return "Не указано"