import os
import time
import sqlite3
from datetime import datetime, timedelta
import speech_recognition as sr
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Lock


AUDIO_FOLDER = "C:/ppython/ermitazh/api_ermitazh/audio"
DB_FILE = "C:/ppython/ermitazh/api_ermitazh/calls.db"
MAX_WAV_AGE_DAYS = 1  


db_lock = Lock()

class AudioHandler(FileSystemEventHandler):
    def __init__(self):
        self.processed_files = set()

    def on_created(self, event):
        if not event.is_directory and (event.src_path.lower().endswith('.mp3') or event.src_path.lower().endswith('.ogg')):
            file_path = event.src_path
            if file_path not in self.processed_files:
                self.processed_files.add(file_path)
                process_file(file_path)

def init_db():
    with db_lock:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT,
                audio_file TEXT,
                text TEXT,
                processed BOOLEAN DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
def convert_to_wav(input_file):
    """Конвертирует MP3/OGG в WAV с удалением исходника"""
    wav_file = os.path.splitext(input_file)[0] + '.wav'
    
    if input_file.lower().endswith('.mp3'):
        os.system(f'ffmpeg -i "{input_file}" -acodec pcm_s16le -ar 16000 -ac 1 "{wav_file}"')
    elif input_file.lower().endswith('.ogg'):
        os.system(f'ffmpeg -i "{input_file}" -acodec pcm_s16le -ar 16000 -ac 1 "{wav_file}"')
    
    
    try:
        os.remove(input_file)
        print(f" Удален исходный файл: {os.path.basename(input_file)}")
    except Exception as e:
        print(f" Не удалось удалить {input_file}: {str(e)}")
    
    return wav_file

def clean_old_wav_files():
    """Удаляет WAV-файлы старше MAX_WAV_AGE_DAYS"""
    now = datetime.now()
    for filename in os.listdir(AUDIO_FOLDER):
        if filename.lower().endswith('.wav'):
            file_path = os.path.join(AUDIO_FOLDER, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if (now - file_time) > timedelta(days=MAX_WAV_AGE_DAYS):
                try:
                    os.remove(file_path)
                    print(f" Удален старый WAV: {filename}")
                except Exception as e:
                    print(f" Не удалось удалить {filename}: {str(e)}")

def recognize_speech(wav_file):
    r = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        audio = r.record(source)
        try:
            return r.recognize_google(audio, language="ru-RU")
        except sr.UnknownValueError:
            return "Речь не распознана"
        except sr.RequestError:
            return "Ошибка сервиса распознавания"

def process_file(file_path):
    try:
        print(f"\n Обнаружен новый файл: {os.path.basename(file_path)}")
        time.sleep(2)  
        
        wav_path = convert_to_wav(file_path)
        text = recognize_speech(wav_path)
        
        with db_lock:
            conn = sqlite3.connect(DB_FILE, check_same_thread=False)
            conn.execute('''
                INSERT INTO calls (time, audio_file, text)
                VALUES (?, ?, ?)
            ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), wav_path, text))
            conn.commit()
            conn.close()
        
        print(f" Успешно обработан. Текст: {text[:100]}...")
        
        
        clean_old_wav_files()
        
        return True
        
    except Exception as e:
        print(f" Ошибка: {str(e)}")
        return False

if __name__ == "__main__":
    print(" Сервис мониторинга папки запущен...")
    print(f" Отслеживается папка: {AUDIO_FOLDER}")
    print(f" Будут удаляться WAV-файлы старше {MAX_WAV_AGE_DAYS} дней")
    print("Нажмите Ctrl+C для остановки\n")
    
    init_db()
    
    
    clean_old_wav_files()
    
    event_handler = AudioHandler()
    observer = Observer()
    observer.schedule(event_handler, AUDIO_FOLDER, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        print("\n Сервис остановлен")