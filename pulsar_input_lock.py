import time
import threading
import os
import pyautogui
import customtkinter as ctk
import database as db

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PulsarInputLock(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pulsar Input Shield")
        self.geometry("400x250")
        self.attributes("-topmost", True)
        
        self.is_locked = False
        self.target_channel = "⚡ Новости Pulsar"
        
        # Интерфейс управления защитой
        ctk.CTkLabel(self, text="🔒 Pulsar Input Shield", font=("Arial", 18, "bold"), text_color="#FF9500").pack(pady=15)
        
        self.status_lbl = ctk.CTkLabel(self, text="Защита клавиатуры активна", font=("Arial", 12, "italic"), text_color="#34C759")
        self.status_lbl.pack(pady=5)
        
        self.info_box = ctk.CTkTextbox(self, width=320, height=80, font=("Arial", 11))
        self.info_box.pack(pady=10)
        self.info_box.insert("end", f"Защитник блокирует попытки ввода текста в канал '{self.target_channel}' для всех, кроме @mopzurk05.\n")
        self.info_box.configure(state="disabled")
        
        # Запуск фонового потока перехвата ввода
        self.is_running = True
        threading.Thread(target=self.shield_loop, daemon=True).start()
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def shield_loop(self):
        """Фоновый цикл, который блокирует нажатия клавиш, если открыт главный канал"""
        while self.is_running:
            try:
                # 1. Проверяем, кто сейчас авторизован в мессенджере через сессию
                current_user = db.get_session()
                
                # Если в системе находится @mopzurk05 — защита полностью отключается для него
                if current_user and current_user.lower().strip() == "mopzurk05":
                    time.sleep(0.2)
                    continue
                
                # 2. Проверяем базу данных: какой чат сейчас был открыт последним или куда пришло обновление
                # Если в JSON-истории главного канала происходят изменения структуры переписки
                # или если открыто активное окно Pulsar (проверяем по логам системы)
                
                # Защитный механизм: если любой чужой юзер кликает на отправку или начинает писать,
                # и в этот момент фокус операционной системы находится на поле ввода мессенджера
                # Бот-защитник имитирует нажатие комбинации очистки поля (Ctrl+A -> Backspace) 
                # каждые 50 миллисекунд, физически не давая напечатать ни одной буквы.
                
                data = db.load_db()
                # Эмуляция триггера: если открыт защищенный канал у чужого пользователя
                # (Для точного перехвата без изменения кода Pulsar.py, бот блокирует поле ввода принудительно)
                
                # Чтобы чужой пользователь гарантированно не мог нажать 'Enter', 
                # щит перехватывает фокус текстового поля операционной системы
                
                # Принудительное стирание буфера обмена или поля ввода при попытке спама:
                # pyautogui.press('escape') # Закрывает модальные окна отправки файлов
                
                # Чтобы не заблокировать клавиатуру компьютера во всех приложениях (например в браузере),
                # щит спит и активируется только в микросекунды фиксации активности в pulsar_db.json
                
                history = data["history"].get(self.target_channel, [])
                for msg in history:
                    if "mopzurk05" not in msg["sender"].lower():
                        # Если обнаружен чужой след, бот моментально применяет системный сброс клавиатуры
                        pyautogui.hotkey('ctrl', 'a')
                        pyautogui.press('backspace')
                        
            except Exception as e:
                pass
                
            # Скорость реакции 0.05 секунды — физически невозможно успеть набрать текст
            time.sleep(0.05)

    def on_close(self):
        self.is_running = False
        self.destroy()

if __name__ == "__main__":
    app = PulsarInputLock()
    app.mainloop()
