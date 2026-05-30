import customtkinter as ctk
import database as db
from tkinter import messagebox

class PulsarChannelSettings(ctk.CTkToplevel):
    def __init__(self, channel_name, parent_app):
        super().__init__()
        self.channel_name = channel_name
        self.app = parent_app
        self.title("Настройки публикации")
        self.geometry("380x250")
        self.attributes("-topmost", True)
        
        ctk.CTkLabel(self, text=f"📢 Настройки канала:\n{channel_name}", font=("Arial", 14, "bold")).pack(pady=15)
        
        # Загружаем текущий режим из базы данных
        current_db = db.load_db()
        channel_data = current_db["groups"].get(channel_name, {})
        current_mode = channel_data.get("post_mode", "channel") # По умолчанию от имени канала
        
        ctk.CTkLabel(self, text="Публиковать посты от имени:", font=("Arial", 12)).pack(pady=5)
        
        self.mode_var = ctk.StringVar(value=current_mode)
        
        ctk.CTkRadioButton(self, text="📢 Названия канала (Анонимно)", variable=self.mode_var, value="channel").pack(pady=4)
        ctk.CTkRadioButton(self, text="👤 Своего личного аккаунта", variable=self.mode_var, value="personal").pack(pady=4)
        
        ctk.CTkButton(self, text="💾 Сохранить настройки", fg_color="#34C759", command=self.save_settings).pack(pady=25)

    def save_settings(self):
        current_db = db.load_db()
        if self.channel_name in current_db["groups"]:
            current_db["groups"][self.channel_name]["post_mode"] = self.mode_var.get()
            db.save_db(current_db)
            messagebox.showinfo("Успех", "Режим публикации успешно изменен!")
            self.destroy()
