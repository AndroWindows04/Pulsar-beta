import customtkinter as ctk
import database as db

class PulsarSearchEngine(ctk.CTkToplevel):
    def __init__(self, chat_name, box_msg_widget, render_engine, current_user, app_context):
        super().__init__()
        self.chat_name = chat_name
        self.box_msg = box_msg_widget
        self.render = render_engine
        self.current_user = current_user
        self.app = app_context
        
        self.title(f"Поиск в: {chat_name}")
        self.geometry("400x120")
        self.attributes("-topmost", True)
        
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.pack(fill="x", padx=15, pady=20)
        
        self.search_entry = ctk.CTkEntry(sf, placeholder_text="Введите текст для поиска в чате...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        
        ctk.CTkButton(sf, text="🔍", width=40, command=self.perform_search).pack(side="right")

    def perform_search(self):
        query = self.search_entry.get().strip().lower()
        if not query: return
        
        # Очищаем экран сообщений
        for w in self.box_msg.winfo_children(): w.destroy()
        
        # Ищем совпадения в базе данных
        messages = db.load_db()["history"].get(self.chat_name, [])
        for idx, msg in enumerate(messages):
            # Если текст сообщения содержит поисковый запрос
            if query in msg["text"].lower():
                is_own = (msg["sender"] == self.current_user)
                display_sender = "Вы" if is_own else f"@{msg['sender']}"
                
                # Подсвечиваем найденные сообщения специальной пометкой [НАЙДЕНО]
                text_to_show = f"🔍 [Найдено] {msg['text']}"
                self.render.draw_bubble(self.box_msg, display_sender, text_to_show, is_own, idx, self.app)
