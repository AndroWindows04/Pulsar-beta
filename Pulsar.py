import sys
import os

LOG_FILE = "pulsar_error_log.txt"

try:
    import customtkinter as ctk
    import database as db
    import media
    from pulsar_ui_components import PulsarUI
    from pulsar_render_engine import PulsarRenderEngine as render
    from pulsar_msg_manager import PulsarMsgManager as msg_mgr
    from pulsar_voice_recorder import PulsarVoiceRecorder
    from pulsar_channel_creator import PulsarChannelCreator
    from pulsar_chat_seeker import PulsarChatSeeker
    from pulsar_ban_manager import PulsarBanManager
    from pulsar_kick_manager import PulsarKickManager
    from pulsar_admin_promoter import PulsarAdminPromoter
    from pulsar_action_panel import PulsarActionPanel

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    class PulsarApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Pulsar")
            self.geometry("1150x700")
            self.current_user = None
            self.active_chat = None
            
            self.recorder = PulsarVoiceRecorder()
            self.container = ctk.CTkFrame(self)
            self.container.pack(fill="both", expand=True)
            
            self.ui = PulsarUI(self)
            self.right_p = None
            
            saved_user = db.get_session()
            if saved_user and saved_user in db.load_db()["users"]:
                self.current_user = saved_user
                self.show_messenger()
            else:
                self.ui.draw_auth()

        def show_messenger(self):
            self.ui.draw_main_messenger()
            self.build_right_panel()
            self.render_chats_list()

        def render_chats_list(self):
            for w in self.scroll_chats_list.winfo_children(): w.destroy()
            current_db = db.load_db()
            
            ctk.CTkButton(self.scroll_chats_list, text="➕ Создать группу/канал", fg_color="#34C759", font=("Arial", 12, "bold"), 
                          command=lambda: PulsarChannelCreator(self)).pack(fill="x", padx=5, pady=8)
            
            for g_key, g_val in current_db["groups"].items():
                f = ctk.CTkFrame(self.scroll_chats_list, fg_color="transparent")
                f.pack(fill="x", pady=2)
                ava = render.get_avatar(g_val.get("avatar"), size=30)
                if ava: ctk.CTkLabel(f, image=ava, text="").pack(side="left", padx=5)
                
                count = f"{len(g_val['members'])} {self.ui.t('members')}" if g_val["type"] == "group" else f"{len(g_val['subscribers'])} {self.ui.t('subscribers')}"
                ctk.CTkButton(f, text=f"{'👥' if g_val['type'] == 'group' else '📢'} {g_key} ({count})", anchor="w", fg_color="transparent", command=lambda k=g_key: self.load_chat(k, "group")).pack(side="left", fill="x", expand=True)
                
            for chat_title in current_db["history"].keys():
                if chat_title.startswith("💬") or chat_title == "Избранное":
                    display_name = self.ui.t("saved") if chat_title == "Избранное" else chat_title
                    ctk.CTkButton(self.scroll_chats_list, text=display_name, anchor="w", fg_color="transparent", command=lambda t=chat_title: self.load_chat(t, "dm")).pack(fill="x", pady=2)

        def build_right_panel(self):
            if self.right_p: return
            
            self.right_p = ctk.CTkFrame(self.container, fg_color="#1C1C1E", corner_radius=0)
            self.right_p.pack(side="right", fill="both", expand=True)
            
            head = ctk.CTkFrame(self.right_p, height=60, fg_color="#2C2C2E", corner_radius=0)
            head.pack(fill="x")
            
            self.lbl_title = ctk.CTkLabel(head, text=self.ui.t("select"), font=("Arial", 16, "bold"))
            self.lbl_title.pack(side="left", padx=20, pady=15)
            
            self.btn_search_inside = ctk.CTkButton(head, text="🔍 Найти в чате", fg_color="#2C2C2E", width=110, 
                                                   command=lambda: PulsarChatSeeker(self.active_chat["name"], self.box_msg, render, self.current_user, self))
            
            self.btn_ban = ctk.CTkButton(head, text="🚫 Бан", fg_color="#FF453A", width=70, command=lambda: PulsarBanManager(self.active_chat["name"], self))
            self.btn_kick = ctk.CTkButton(head, text="🚪 Кик", fg_color="#FF9500", text_color="black", width=70, command=lambda: PulsarKickManager(self.active_chat["name"], self))
            self.btn_promote = ctk.CTkButton(head, text="👑 Admin", fg_color="#34C759", width=80, command=lambda: PulsarAdminPromoter(self.active_chat["name"], self))
            self.btn_chat_ava = ctk.CTkButton(head, text=self.ui.t("chat_ava"), fg_color="#3A3A3C", width=110, command=self.change_chat_avatar)
            
            self.box_msg = ctk.CTkScrollableFrame(self.right_p, fg_color="transparent")
            self.box_msg.pack(fill="both", expand=True, padx=15, pady=15)
            
            input_f = ctk.CTkFrame(self.right_p, fg_color="transparent")
            input_f.pack(fill="x", side="bottom", padx=15, pady=15)
            
            ctk.CTkButton(input_f, text="📎", width=45, height=45, fg_color="#3A3A3C", command=self.send_file).pack(side="left", padx=(0,5))
            
            self.btn_voice = ctk.CTkButton(input_f, text="🎙️", width=45, height=45, fg_color="#FF453A", text_color="white", command=self.toggle_voice_record)
            self.btn_voice.pack(side="left", padx=(0,10))
            
            self.e_msg = ctk.CTkEntry(input_f, placeholder_text=self.ui.t("placeholder"), height=45)
            self.e_msg.pack(side="left", fill="x", expand=True, padx=(0,10))
            self.e_msg.bind("<Return>", lambda event: self.send_text())
            
            ctk.CTkButton(input_f, text="➡", width=50, height=45, command=self.send_text).pack(side="right")

        def toggle_voice_record(self):
            if not self.active_chat: return
            if not self.recorder.is_recording:
                self.recorder.start_recording()
                self.btn_voice.configure(fg_color="#34C759", text="🛑")
                self.e_msg.configure(placeholder_text="🔴 Запись голосового сообщения...")
                self.e_msg.configure(state="disabled")
            else:
                voice_path = self.recorder.stop_recording()
                self.btn_voice.configure(fg_color="#FF453A", text="🎙️")
                self.e_msg.configure(state="normal")
                self.e_msg.configure(placeholder_text=self.ui.t("placeholder"))
                if voice_path:
                    db.save_message(self.active_chat["name"], self.current_user, f"📎 {voice_path}")
                    self.refresh_messages_view()

        def load_chat(self, name, c_type):
            self.active_chat = {"name": name, "type": c_type}
            self.lbl_title.configure(text=self.ui.t("saved") if name == "Избранное" else name)
            self.refresh_messages_view()
            
            self.btn_search_inside.pack(side="right", padx=3)
            
            if c_type == "group":
                g = db.load_db()["groups"].get(name, {})
                if self.current_user == g.get("owner") or self.current_user in g.get("admins", []):
                    self.btn_ban.pack(side="right", padx=3)
                    self.btn_kick.pack(side="right", padx=3)
                    self.btn_promote.pack(side="right", padx=3)
                    self.btn_chat_ava.pack(side="right", padx=3)
                    return
            
            self.btn_ban.pack_forget()
            self.btn_kick.pack_forget()
            self.btn_promote.pack_forget()
            self.btn_chat_ava.pack_forget()

        def refresh_messages_view(self):
            if not self.active_chat: return
            for w in self.box_msg.winfo_children(): w.destroy()
            messages = db.load_db()["history"].get(self.active_chat["name"], [])
            for idx, msg in enumerate(messages):
                if "hidden_for" in msg and self.current_user in msg["hidden_for"]:
                    continue
                is_own = (msg["sender"] == self.current_user)
                render.draw_bubble(self.box_msg, self.ui.t("you") if is_own else f"@{msg['sender']}", msg["text"], is_own, idx, self)

        def send_text(self):
            t = self.e_msg.get().strip()
            if t and self.active_chat:
                db.save_message(self.active_chat["name"], self.current_user, t)
                self.e_msg.delete(0, "end")
                self.refresh_messages_view()

        def send_file(self):
            if not self.active_chat: return
            from tkinter import filedialog
            path = filedialog.askopenfilename(filetypes=[("Медиафайлы", "*.mp3 *.wav *.png *.jpg *.jpeg *.gif *.mp4 *.avi *.mkv *.mov")])
            if path:
                # Превращаем обратные слэши Windows в прямые для стабильности путей
                clean_path = path.replace("\\", "/")
                db.save_message(self.active_chat["name"], self.current_user, f"📎 {clean_path}")
                self.refresh_messages_view()

        def open_message_actions(self, msg_index, current_text, is_media):
            PulsarActionPanel(self, self.active_chat["name"], msg_index, current_text, is_media)

        def change_chat_avatar(self):
            if self.active_chat and self.active_chat["type"] == "group":
                db.update_avatar("group", self.active_chat["name"], media.choose_avatar())
                self.render_chats_list()

        def clear_screen(self):
            for w in self.container.winfo_children():
                if w != self.right_p:
                    w.destroy()

    if __name__ == "__main__":
        app = PulsarApp()
        app.mainloop()

except Exception as e:
    import traceback
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== Pulsar Error Log ===\n")
f.write(f"Тип ошибки: {type(e).name}\n")
f.write(f"Описание: {str(e)}\n\n")
f.write("=== Полный Traceback ===\n")
traceback.print_exc(file=f)
print(f"❌ Сбой. Лог сохранен в: {os.path.abspath(LOG_FILE)}")
