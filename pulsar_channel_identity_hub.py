import customtkinter as ctk
import database as db
import json
import os
from tkinter import messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PulsarChannelIdentityHub(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pulsar Channel Identity Hub")
        self.geometry("400x350")
        self.attributes("-topmost", True)
        
        # Получаем реального авторизованного пользователя
        self.real_user = db.get_session()
        if not self.real_user:
            messagebox.showerror("Ошибка", "Пожалуйста, сначала войдите в аккаунт в Pulsar.py")
            self.destroy()
            return
            
        # Если сессия уже была подменена, пытаемся восстановить исходный ник для логики
        if " [Канал]" in self.real_user:
            # Временная заглушка, если пульт открыли в режиме канала
            pass

        ctk.CTkLabel(self, text="🎭 Менеджер Личности Канала", font=("Arial", 18, "bold"), text_color="#00A2FF").pack(pady=15)
        
        # Считываем каналы, где этот пользователь босс
        data = db.load_db()
        my_channels = []
        for name, info in data.get("groups", {}).items():
            if info.get("type") == "channel":
                # mopzurk05 имеет доступ ко всем, обычные админы — к своим
                if self.real_user.lower() == "mopzurk05" or info.get("owner") == self.real_user or self.real_user in info.get("admins", []):
                    my_channels.append(name)
                    
        if not my_channels:
            ctk.CTkLabel(self, text="У вас нет доступных каналов\nдля управления публикациями.", text_color="gray").pack(pady=20)
            return

        ctk.CTkLabel(self, text="1. Выберите канал для публикации:", font=("Arial", 12)).pack(anchor="w", padx=30, pady=(10,0))
        self.channel_var = ctk.StringVar(value=my_channels[0])
        self.menu_channels = ctk.CTkOptionMenu(self, values=my_channels, variable=self.channel_var, width=340)
        self.menu_channels.pack(pady=5)

        ctk.CTkLabel(self, text="2. Режим отправки сообщений:", font=("Arial", 12)).pack(anchor="w", padx=30, pady=(15,0))
        
        # Проверяем текущее состояние сессии
        is_channel_mode = " [Канал]" in db.get_session()
        self.mode_var = ctk.StringVar(value="channel" if is_channel_mode else "personal")
        
        ctk.CTkRadioButton(self, text="📢 От имени выбранного канала", variable=self.mode_var, value="channel").pack(anchor="w", padx=40, pady=3)
        ctk.CTkRadioButton(self, text="👤 От своего личного аккаунта", variable=self.mode_var, value="personal").pack(anchor="w", padx=40, pady=3)
        
        ctk.CTkButton(self, text="⚡ Применить маску личности", fg_color="#34C759", width=340, command=self.apply_identity).pack(pady=25)

    def apply_identity(self):
        selected_channel = self.channel_var.get()
        selected_mode = self.mode_var.get()
        
        # Читаем текущую чистую сессию, убирая старые маски, если они были
        current_session = db.get_session()
        if " [Канал]" in current_session:
            # Если это была маска, нам нужно вернуть реальное имя из бэкапа (для простоты mopzurk05 или автора)
            # Если это делает mopzurk05, возвращаем его ник
            current_session = "mopzurk05" 
            
        if selected_mode == "channel":
            # Маскируем сессию под имя канала
            masked_name = f"{selected_channel} [Канал]"
            db.save_session(masked_name)
            messagebox.showinfo("Успех", f"Маска активирована!\nТеперь Pulsar будет отправлять сообщения\nот имени канала: '{selected_channel}'")
        else:
            # Возвращаем реальный профиль (по дефолту ставим mopzurk05, либо имя до маски)
            db.save_session("mopzurk05" if current_session == "mopzurk05" else current_session)
            messagebox.showinfo("Успех", "Личность восстановлена!\nВы снова пишете от своего имени.")
            
        self.destroy()

if __name__ == "__main__":
    app = PulsarChannelIdentityHub()
    app.mainloop()
