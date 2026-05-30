import time
import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DB_FILE = "pulsar_db.json"
TARGET_CHANNEL = "⚡ Новости Pulsar"

class InstantValidationHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.last_processed_time = 0

    def on_modified(self, event):
        # Проверяем, что изменился именно файл базы данных Pulsar
        if os.path.basename(event.src_path) == DB_FILE:
            # Защита от двойных системных триггеров Windows (дребезг контактов диска)
            current_time = time.time()
            if current_time - self.last_processed_time < 0.05:
                return
            self.last_processed_time = current_time
            
            # Запускаем моментальную валидацию
            self.validate_database()

    def validate_database(self):
        try:
            # Читаем базу данных бинарным методом для максимальной скорости
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            history = data.get("history", {}).get(TARGET_CHANNEL, [])
            if not history:
                return
                
            modified = False
            cleaned_history = []
            
            # Сканируем последнее отправленное сообщение
            for msg in history:
                sender = msg.get("sender", "").lower().strip()
                
                # Проверяем, принадлежит ли сообщение автору mopzurk05
                if "mopzurk05" in sender:
                    cleaned_history.append(msg)
                else:
                    # Если написал чужой — фиксируем нелегальный пост
                    modified = True
                    print(f"[{time.strftime('%H:%M:%S')}] 💥 МГНОВЕННЫЙ ПЕРЕХВАТ: Удален пост от @{msg.get('sender')}")
            
            # Если нашли чужой пост — мгновенно перезаписываем файл, стирая его из базы
            if modified:
                data["history"][TARGET_CHANNEL] = cleaned_history
                with open(DB_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                    
        except Exception as e:
            # Ошибка может возникнуть, если Pulsar.py еще не закончил запись, просто пропускаем кадр
            pass

def start_gatekeeper():
    print("==================================================")
    print("🚀 Pulsar Ultra-Fast Gatekeeper успешно запущен!")
    print(f"🔒 Ведется прямое слежение за ядром диска для: {TARGET_CHANNEL}")
    print("==================================================")
    
    event_handler = InstantValidationHandler()
    observer = Observer()
    # Запускаем наблюдение за текущей директорией проекта
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_gatekeeper()
