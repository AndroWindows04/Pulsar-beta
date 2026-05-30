import database as db

class PulsarMsgManager:
    @staticmethod
    def edit_text(chat_name, msg_index, new_text, sender):
        """Проверяет права автора и изменяет текст сообщения"""
        data = db.load_db()
        if chat_name in data["history"]:
            history = data["history"][chat_name]
            if 0 <= msg_index < len(history):
                msg = history[msg_index]
                if msg["sender"] == sender and not msg["text"].startswith("📎"):
                    msg["text"] = new_text
                    db.save_db(data)
                    return True
        return False

    @staticmethod
    def delete_item(chat_name, msg_index, sender, delete_for_all=True):
        """Удаляет любой текст или медиа из истории чата"""
        return db.delete_message(chat_name, msg_index, sender, delete_for_all)
