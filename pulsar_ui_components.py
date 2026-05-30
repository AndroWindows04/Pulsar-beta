import customtkinter as ctk
import database as db
import media
from pulsar_render_engine import PulsarRenderEngine as render

LANGUAGES = {
    "ru": {
        "name": "Имя", "surname": "Фамилия", "username": "Никнейм", "pass": "Пароль", "login": "Войти", "reg": "Регистрация",
        "busy": "Занято/Ошибка!", "search": "Поиск @username...", "saved": "🔖 Избранное", "chat_title": "ЧАТЫ И КАНАЛЫ",
        "select": "Выберите чат", "manage": "⚙️ Управление", "placeholder": "Сообщение...", "settings": "⚙️ Настройки",
        "logout": "🚪 Выйти", "save": "Сохранить", "not_found": "Не найдено", "you": "Вы", "chat_ava": "🖼️ Ава чата"
    },
    "en": {
        "name": "Name", "surname": "Surname", "username": "Username", "pass": "Password", "login": "Login", "reg": "Register",
        "busy": "Error/Taken!", "search": "Search @username...", "saved": "🔖 Saved Messages", "chat_title": "CHATS & CHANNELS",
        "select": "Select a chat", "manage": "⚙️ Manage", "placeholder": "Message...", "settings": "⚙️ Settings",
        "logout": "🚪 Logout", "save": "Save", "not_found": "Not found", "you": "You", "chat_ava": "🖼️ Chat Ava"
    },
    "uk": {
        "name": "Ім'я", "surname": "Прізвище", "username": "Нікнейм", "pass": "Пароль", "login": "Увійти", "reg": "Реєстрація",
        "busy": "Зайнято/Помилка!", "search": "Пошук @username...", "saved": "🔖 Обране", "chat_title": "ГРУПИ ТА КАНАЛИ",
        "select": "Оберіть чат", "manage": "⚙️ Керування", "placeholder": "Повідомлення...", "settings": "⚙️ Налаштування",
        "logout": "🚪 Вийти", "save": "Зберегти", "not_found": "Не знадено", "you": "Ви", "chat_ava": "🖼️ Ава чату"
    }
}

class PulsarUI:
    def __init__(self, app):
        self.app = app
        self.lang = "ru"

    def t(self, key):
        return LANGUAGES[self.lang].get(key, key)

    def draw_auth(self):
        self.app.clear_screen()
        box = ctk.CTkFrame(self.app.container, width=400, height=550, corner_radius=15)
        box.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(box, text="⚡ Pulsar", font=("Arial", 28, "bold"), text_color="#00A2FF").pack(pady=10)
        
        lf = ctk.CTkFrame(box, fg_color="transparent")
        lf.pack(pady=5)
        for c, n in [("ru", "RU"), ("en", "EN"), ("uk", "UA")]:
            ctk.CTkButton(lf, text=n, width=40, height=25, fg_color="#3A3A3C" if self.lang != c else "#007AFF", command=lambda x=c: self.change_lang_init(x)).pack(side="left", padx=2)

        e_user = ctk.CTkEntry(box, placeholder_text=self.t("username"), width=300)
        e_user.pack(pady=4)
        e_pass = ctk.CTkEntry(box, placeholder_text=self.t("pass"), show="*", width=300)
        e_pass.pack(pady=4)
        
        lbl_err = ctk.CTkLabel(box, text="", text_color="red")
        lbl_err.pack()

        def sign_in():
            res, data = db.login_user(e_user.get(), e_pass.get())
            if res: self.app.current_user = data; self.app.show_messenger()
            else: lbl_err.configure(text=data)

        def sign_up():
            win = ctk.CTkToplevel(self.app)
            win.geometry("350x450"); win.attributes("-topmost", True)
            ctk.CTkLabel(win, text=self.t("reg"), font=("Arial", 16, "bold")).pack(pady=10)
            en = ctk.CTkEntry(win, placeholder_text=self.t("name"))
            en.pack(pady=4)
            es = ctk.CTkEntry(win, placeholder_text=self.t("surname"))
            es.pack(pady=4)
            eu = ctk.CTkEntry(win, placeholder_text=self.t("username"))
            eu.pack(pady=4)
            ep = ctk.CTkEntry(win, placeholder_text=self.t("pass"), show="*")
            ep.pack(pady=4)
            
            def do_reg():
                ok, d = db.register_user(eu.get(), en.get(), es.get(), ep.get())
                if ok: self.app.current_user = d; win.destroy(); self.app.show_messenger()
            ctk.CTkButton(win, text="OK", command=do_reg).pack(pady=15)

        ctk.CTkButton(box, text=self.t("login"), width=300, command=sign_in).pack(pady=5)
        ctk.CTkButton(box, text=self.t("reg"), width=300, fg_color="#2C2C2E", command=sign_up).pack(pady=5)

    def change_lang_init(self, code):
        self.lang = code
        self.draw_auth()

    def draw_main_messenger(self):
        self.app.clear_screen()
        u_data = db.load_db()["users"][self.app.current_user]
        self.lang = u_data.get("lang", "ru")
        
        left_p = ctk.CTkFrame(self.app.container, width=320, corner_radius=0)
        left_p.pack(side="left", fill="y")
        
        prof_f = ctk.CTkFrame(left_p, fg_color="transparent")
        prof_f.pack(fill="x", pady=10, padx=15)
        
        ava = render.get_avatar(u_data.get("avatar"))
        ctk.CTkLabel(prof_f, image=ava, text="" if ava else "👤", font=("Arial", 20)).pack(side="left", padx=5)
        ctk.CTkLabel(prof_f, text=f"@{self.app.current_user}", font=("Arial", 14, "bold"), text_color="#00A2FF").pack(side="left")
        ctk.CTkButton(prof_f, text="⚙️", width=30, command=self.open_settings_modal).pack(side="right")

        sf = ctk.CTkFrame(left_p, fg_color="transparent")
        sf.pack(fill="x", padx=10, pady=5)
        e_search = ctk.CTkEntry(sf, placeholder_text=self.t("search"))
        e_search.pack(side="left", fill="x", expand=True, padx=(0,5))
        
        def find():
            res = db.search_and_create_chat(e_search.get())
            if res["found"]: self.app.render_chats_list(); self.app.load_chat(res["title"], "dm")
            else: self.app.lbl_title.configure(text=self.t("not_found"))
        ctk.CTkButton(sf, text="🔍", width=40, command=find).pack(side="right")
        
        ctk.CTkButton(left_p, text=self.t("saved"), fg_color="#2C2C2E", anchor="w", command=lambda: self.app.load_chat("Избранное", "saved")).pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(left_p, text=self.t("chat_title"), font=("Arial", 11, "bold"), text_color="gray").pack(padx=15, anchor="w")
        
        self.app.scroll_chats_list = ctk.CTkScrollableFrame(left_p, fg_color="transparent")
        self.app.scroll_chats_list.pack(fill="both", expand=True, padx=5, pady=5)

    def open_settings_modal(self):
        win = ctk.CTkToplevel(self.app)
        win.title(self.t("settings")); win.geometry("380x520"); win.attributes("-topmost", True)
        
        ctk.CTkButton(win, text=self.t("change_ava"), command=lambda: [db.update_avatar("user", self.app.current_user, media.choose_avatar()), self.app.show_messenger(), win.destroy()]).pack(pady=10)
        
        ctk.CTkLabel(win, text=self.t("username")).pack()
        en = ctk.CTkEntry(win, placeholder_text=f"@{self.app.current_user}")
        en.pack()
        
        ctk.CTkLabel(win, text=self.t("pass")).pack()
        ep = ctk.CTkEntry(win, placeholder_text="****", show="*")
        ep.pack()
        
        le = ctk.CTkLabel(win, text="", text_color="red"); le.pack()
        
        def save():
            ok, data = db.change_user_data(self.app.current_user, en.get(), ep.get(), self.lang)
            if ok: self.app.current_user = data; self.app.show_messenger(); win.destroy()
            else: le.configure(text=self.t("busy"))

        ctk.CTkButton(win, text=self.t("save"), fg_color="#34C759", command=save).pack(pady=10)
        
        lf = ctk.CTkFrame(win, fg_color="transparent"); lf.pack(pady=10)
        for c, n in [("ru", "RU"), ("en", "EN"), ("uk", "UA")]:
            ctk.CTkButton(lf, text=n, width=50, fg_color="#3A3A3C" if self.lang != c else "#007AFF", command=lambda x=c: [setattr(self, 'lang', x), db.change_user_data(self.app.current_user, "", "", x), self.app.show_messenger(), win.destroy()]).pack(side="left", padx=2)
            
        ctk.CTkButton(win, text=self.t("logout"), fg_color="#FF453A", command=lambda: [db.clear_session(), win.destroy(), self.draw_auth()]).pack(side="bottom", pady=20)
