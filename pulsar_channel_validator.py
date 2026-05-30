import database as db
from tkinter import messagebox

class PulsarChannelValidator:
    TARGET_CHANNEL = "⚡ Новости Pulsar"

    @classmethod
    def validate_before_send(cls, chat_name, sender_username, text_content):
        """
        Проверяет сообщение ДО отправки на экран и в базу.
        Возвращает True, если отправка разрешена, и False, если заблокирована.
        """
        # Если отправка идет НЕ в главный канал — разрешаем без проверок
        if chat_name != cls.TARGET_CHANNEL:
            return True

        # Приводим никнейм к чистому виду для проверки
        clean_sender = sender_username.lower().strip()

        # Разрешаем отправку ТОЛЬКО если в нике есть mopzurk05
        if "mopzurk05" in clean_sender:
            return True

        # Если пишет кто-то другой — выдаем моментальный отказ
        messagebox.showerror(
            "🔒 Ошибка доступа Pulsar", 
            "Внимание! Публикация постов в главный канал разрешена исключительно суперпользователю @mopzurk05.\n\nВаше сообщение заблокировано защитной системой Gatekeeper."
        )
        return False
