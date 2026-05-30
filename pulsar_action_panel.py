import customtkinter as ctk
import database as db
from pulsar_msg_manager import PulsarMsgManager as msg_mgr

class PulsarActionPanel(ctk.CTkToplevel):
    def __init__(self, parent_app, chat_name, msg_index, current_text, is_media):
        super().__init__()
        self.app = parent_app
        self.chat_name = chat_name
        self.msg_index = msg_index
        self.current_user = parent_app.current_user
        
        self.title("Действия с сообщением")
        self.geometry("340x280")
        self.attributes("-topmost", True)
        
        ctk.CTkLabel(self, text="⚙️ Управление сообщением", font=("Arial", 14, "bold")).pack(pady=10)

        # Окно изменения текста (только если это не медиа-файл)
        if not is_media:
            ctk.CTkLabel(self, text="Редактировать текст:").pack()
            self.edit_entry = ctk.CTkEntry(self, width=280)
            self.edit_entry.insert(0, current_text)
            self.edit_entry.pack(pady=5)
            
            ctk.CTkButton(self, text="📝 Изменить для всех", fg_color="#FF9500", text_color="black", command=self.apply_edit).pack(pady=2)

        # Кнопки удаления
        ctk.CTkButton(self, text="🗑️ Удалить ТОЛЬКО У СЕБЯ", fg_color="#3A3A3C", command=self.delete_only_me).pack(pady=(15, 4))
        ctk.CTkButton(self, text="🚨 Удалить У ВСЕХ (Из базы)", fg_color="#FF453A", command=self.delete_for_everyone).pack(pady=2)

    def apply_edit(self):
        new_text = self.edit_entry.get().strip()
        if new_text:
            db.edit_message(self.chat_name, self.msg_index, new_text, self.current_user)
            self.app.refresh_messages_view()
            self.destroy()

    def delete_only_me(self):
        # Передаем параметр delete_for_all=False в базу данных
        db.delete_message(self.chat_name, self.msg_index, self.current_user, delete_for_all=False)
        self.app.refresh_messages_view()
        self.destroy()

    def delete_for_everyone(self):
        # Вызов классического удаления из базы данных
        db.delete_message(self.chat_name, self.msg_index, self.current_user, delete_for_all=True)
        self.app.refresh_messages_view()
        self.destroy()
