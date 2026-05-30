import customtkinter as ctk
import database as db
from tkinter import messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PulsarModeratorPanel(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pulsar SuperAdmin Panel")
        self.geometry("450x500")
        self.attributes("-topmost", True)
        
        # Защитная проверка на суперпользователя
        current_session_user = db.get_session()
        if not current_session_user or current_session_user.lower().strip() != "mopzurk05":
            self.draw_access_denied()
            return

        self.draw_admin_panel()

    def draw_access_denied(self):
        lbl = ctk.CTkLabel(self, text="🔒 ДОСТУП ОГРАНИЧЕН", font=("Arial", 18, "bold"), text_color="#FF453A")
        lbl.pack(pady=40)
        lbl_desc = ctk.CTkLabel(self, text="Этот пульт доступен только разработчику @mopzurk05.\nАвторизуйтесь в Pulsar под своим никнеймом.", font=("Arial", 12))
        lbl_desc.pack(pady=10)
        ctk.CTkButton(self, text="Закрыть", fg_color="#3A3A3C", command=self.destroy).pack(pady=30)

    def draw_admin_panel(self):
        data = db.load_db()
        
        ctk.CTkLabel(self, text="👑 Пульт Верификации Pulsar", font=("Arial", 20, "bold"), text_color="#00A2FF").pack(pady=20)
        ctk.CTkLabel(self, text="Администратор: @mopzurk05", font=("Arial", 11, "italic"), text_color="gray").pack(pady=(0, 20))

        # --- БЛОК 1. ВЕРИФИКАЦИЯ КАНАЛОВ И ГРУПП ---
        ctk.CTkLabel(self, text="⚡ Выберите Группу / Канал:", font=("Arial", 13, "bold")).pack(anchor="w", padx=40)
        
        groups_list = list(data.get("groups", {}).keys())
        self.group_var = ctk.StringVar(value=groups_list if groups_list else "")
        self.group_menu = ctk.CTkOptionMenu(self, values=groups_list, variable=self.group_var, width=370)
        self.group_menu.pack(pady=5)
        
        btn_g_verify = ctk.CTkButton(self, text="✔️ Выдать галочку чату", fg_color="#34C759", width=370, command=self.verify_selected_group)
        btn_g_verify.pack(pady=3)

        # --- БЛОК 2. ВЕРИФИКАЦИЯ ДРУГИХ ПОЛЬЗОВАТЕЛЕЙ ---
        ctk.CTkLabel(self, text="👤 Выберите Пользователя:", font=("Arial", 13, "bold")).pack(anchor="w", padx=40, pady=(25, 0))
        
        users_list = list(data.get("users", {}).keys())
        if "mopzurk05" in users_list: users_list.remove("mopzurk05") # mopzurk05 верифицирован лаунчером
        
        self.user_var = ctk.StringVar(value=users_list if users_list else "")
        self.user_menu = ctk.CTkOptionMenu(self, values=users_list, variable=self.user_var, width=370)
        self.user_menu.pack(pady=5)
        
        btn_u_verify = ctk.CTkButton(self, text="✔️ Выдать галочку пользователю", fg_color="#5856D6", width=370, command=self.verify_selected_user)
        btn_u_verify.pack(pady=3)

        # Кнопка сброса
        btn_reset = ctk.CTkButton(self, text="🔄 Сбросить все галочки и имена", fg_color="transparent", text_color="#FF453A", width=370, command=self.reset_all_badges)
        btn_reset.pack(side="bottom", pady=25)

    def verify_selected_group(self):
        target = self.group_var.get()
        if not target: return
        data = db.load_db()
        data["groups"][target]["verified"] = True
        db.save_db(data)
        messagebox.showinfo("Успех", f"Канал '{target}' верифицирован!")

    def verify_selected_user(self):
        target = self.user_var.get()
        if not target: return
        
        data = db.load_db()
        user_info = data["users"][target]
        
        # Если галочки в имени ещё нет — аккуратно приписываем её к Имени в JSON
        if "✔️" not in user_info["name"]:
            user_info["name"] = f"{user_info['name']} ✔️"
            data["users"][target]["verified"] = True
            db.save_db(data)
            messagebox.showinfo("Успех", f"Пользователь @{target} верифицирован!\nГалочка добавлена к его имени.")
        else:
            messagebox.showwarning("Внимание", "Этот пользователь уже имеет галочку!")

    def reset_all_badges(self):
        data = db.load_db()
        # Очищаем каналы
        for g in data.get("groups", {}).values():
            if "verified" in g: g["verified"] = False
        # Очищаем имена пользователей от значка галочки
        for u in data.get("users", {}).values():
            if "verified" in u: u["verified"] = False
            if "✔️" in u["name"]:
                u["name"] = u["name"].replace(" ✔️", "").replace("✔️", "").strip()
                
        db.save_db(data)
        messagebox.showinfo("Сброс", "Все выданные галочки успешно удалены, имена восстановлены!")
        self.destroy()

if __name__ == "__main__":
    app = PulsarModeratorPanel()
    app.mainloop()
