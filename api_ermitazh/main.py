import time
import sqlite3
import logging
from openai import OpenAI
from tonality import TonalityAnalyzer
from bd import save_to_db
from prompt import get_prompt  
from key import api_key

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

CALLS_DB = 'calls.db'
MAIN_DB = 'database_api.db'

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

def init_calls_db():
    """Инициализация базы с вызовами"""
    try:
        with sqlite3.connect(CALLS_DB) as conn:
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time TEXT,
                    audio_file TEXT,
                    text TEXT,
                    processed BOOLEAN DEFAULT 0 NOT NULL
                )
            ''')
            
            
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(calls)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'processed' not in columns:
                conn.execute('ALTER TABLE calls ADD COLUMN processed BOOLEAN DEFAULT 0 NOT NULL')
                logging.info("Добавлен столбец processed в таблицу calls")
            
            conn.commit()
    except Exception as e:
        logging.error(f"Ошибка инициализации БД: {e}")
        raise

def get_unprocessed_calls():
    """Получаем необработанные записи"""
    try:
        with sqlite3.connect(CALLS_DB) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, text 
                FROM calls 
                WHERE processed = 0
                ORDER BY id ASC
            ''')
            return cursor.fetchall()
    except Exception as e:
        logging.error(f"Ошибка получения записей: {e}")
        return []

def mark_as_processed(call_id):
    """Помечаем запись как обработанную ТОЛЬКО при успешном сохранении"""
    try:
        with sqlite3.connect(CALLS_DB) as conn:
            conn.execute('''
                UPDATE calls 
                SET processed = 1 
                WHERE id = ?
            ''', (call_id,))
            conn.commit()
            logging.info(f"Запись {call_id} помечена как обработанная")
    except Exception as e:
        logging.error(f"Ошибка отметки записи {call_id}: {e}")

def process_dialog(text, call_id):
    try:
        logging.info(f"Начата обработка записи {call_id}")
        
        analyzer = TonalityAnalyzer()
        dialog_lines = text.split('\n')
        
        logging.debug("Анализ тональности...")
        sentiment = analyzer.analyze(dialog_lines)
        
        logging.debug("Генерация ответа OpenAI...")
        current_prompt = get_prompt(text)  
        
        completion = client.chat.completions.create(
            extra_body={},
            model="deepseek/deepseek-chat:free",
            messages=[{"role": "user", "content": current_prompt}]  
        )
        
        response = completion.choices[0].message.content
        print(response)
        logging.debug("Сохранение результатов...")
        save_to_db(response, sentiment, call_id)
        mark_as_processed(call_id)  
        
    except Exception as e:
        logging.error(f"Ошибка обработки записи {call_id}: {e}")
        raise
def main_loop():
    """Основной цикл обработки"""
    init_calls_db()
    init_users_db()
    logging.info("Сервис анализа запущен")
    
    while True:
        try:
            logging.debug("Проверка новых записей...")
            unprocessed_calls = get_unprocessed_calls()
            
            if not unprocessed_calls:
                logging.debug("Новых записей не найдено")
                time.sleep(10)
                continue
                
            for call_record in unprocessed_calls:
                call_id = call_record['id']
                call_text = call_record['text']  
                
               
                logging.debug(f"Текст звонка [ID:{call_id}]:\n{call_text}")
                
                if not call_text.strip():
                    logging.warning(f"Пустой текст в записи {call_id}! Пропуск.")
                    mark_as_processed(call_id)
                    continue
                    
                try:
                    process_dialog(call_text, call_id)  
                    mark_as_processed(call_id)
                except Exception as e:
                    logging.error(f"Ошибка обработки: {str(e)}")
                    continue
                    
            time.sleep(5)
            
        except KeyboardInterrupt:
            logging.info("Остановка сервиса...")
            break
        except Exception as e:
            logging.error(f"Критическая ошибка: {str(e)}")
            time.sleep(30)



def init_users_db():
    """Инициализация таблицы Users"""
    try:
        with sqlite3.connect(MAIN_DB) as conn:
            conn.execute('''
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
            conn.commit()
    except Exception as e:
        logging.error(f"Ошибка инициализации Users: {e}")
        raise

if __name__ == "__main__":
    main_loop()