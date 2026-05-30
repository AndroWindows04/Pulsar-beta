import json
import os

DB_FILE = "pulsar_db.json"
SESSION_FILE = "pulsar_session.json"

DEFAULT_DB = {
    "users": {
        "alex99": {"name": "Алексей", "surname": "Иванов", "password": "password123", "avatar": "", "lang": "ru"},
        "durov": {"name": "Павел", "surname": "Дуров", "password": "password123", "avatar": "", "lang": "ru"}
    },
    "groups": {
        "Python Devs": {"owner": "alex99", "admins": [], "members": ["alex99", "durov"], "banned": [], "type": "group", "avatar": ""},
        "⚡ Новости Pulsar": {"owner": "durov", "admins": ["alex99"], "subscribers": ["alex99", "durov"], "banned": [], "type": "channel", "avatar": ""}
    },
    "history": {"Избранное": [], "Python Devs": [], "⚡ Новости Pulsar": []}
}

def load_db():
    if not os.path.exists(DB_FILE):
        save_db(DEFAULT_DB)
        return DEFAULT_DB
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return DEFAULT_DB

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f).get("current_user")
            except: return None
    return None

def save_session(username):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({"current_user": username}, f)

def clear_session():
    if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)

def login_user(username, password):
    db = load_db()
    # Жесткая очистка ника при входе
    username = username.lower().strip().replace("@", "").replace(" ", "")
    if username in db["users"] and db["users"][username]["password"] == password:
        save_session(username)
        return True, username
    return False, "Неверный ник или пароль"

def register_user(username, name, surname, password):
    db = load_db()
    
    # Полная очистка никнейма от пробелов, знаков @ и перевод в нижний регистр
    username = username.lower().strip().replace("@", "").replace(" ", "")
    name = name.strip()
    surname = surname.strip()
    password = password.strip()
    
    if not username or not password or not name or not surname: 
        return False, "Пустые поля!"
        
    # Честная проверка на существование никнейма в базе
    if username in db["users"]: 
        return False, "Занято!"
        
    # Сохраняем пользователя со строго очищенным никнеймом в качестве ключа
    db["users"][username] = {"name": name, "surname": surname, "password": password, "avatar": "", "lang": "ru"}
    save_db(db)
    save_session(username)
    return True, username

def change_user_data(username, new_nick, new_pass, lang_code):
    db = load_db()
    new_nick = new_nick.lower().strip().replace("@", "").replace(" ", "") if new_nick else username
    
    if new_nick != username and new_nick in db["users"]: 
        return False, "Занято!"
    
    user_data = db["users"][username]
    if new_pass: user_data["password"] = new_pass.strip()
    user_data["lang"] = lang_code
    
    if new_nick != username:
        db["users"][new_nick] = db["users"].pop(username)
        save_session(new_nick)
        for g in db["groups"].values():
            if g["owner"] == username: g["owner"] = new_nick
            if username in g["admins"]: g["admins"] = [new_nick if x == username else x for x in g["admins"]]
            if "members" in g and username in g["members"]: g["members"] = [new_nick if x == username else x for x in g["members"]]
            if "subscribers" in g and username in g["subscribers"]: g["subscribers"] = [new_nick if x == username else x for x in g["subscribers"]]
        username = new_nick
        
    save_db(db)
    return True, username

def update_avatar(target_type, target_name, path):
    db = load_db()
    if target_type == "user" and target_name in db["users"]: db["users"][target_name]["avatar"] = path
    elif target_type == "group" and target_name in db["groups"]: db["groups"][target_name]["avatar"] = path
    save_db(db)

def search_and_create_chat(username):
    db = load_db()
    username = username.lower().strip().replace("@", "").replace(" ", "")
    if username in db["users"]:
        u = db["users"][username]
        title = f"💬 {u['name']} {u['surname']} (@{username})"
        if title not in db["history"]:
            db["history"][title] = []
            save_db(db)
        return {"found": True, "title": title}
    return {"found": False, "title": "Не найдено"}

def save_message(chat_name, sender, text):
    db = load_db()
    if chat_name not in db["history"]: db["history"][chat_name] = []
    db["history"][chat_name].append({"sender": sender, "text": text})
    save_db(db)

def manage_member(group_name, member, action):
    db = load_db()
    group = db["groups"].get(group_name)
    if not group: return "Ошибка"
    if action == "ban":
        if member in group.get("members", []): group["members"].remove(member)
        if member in group.get("subscribers", []): group["subscribers"].remove(member)
        if member not in group["banned"]: group["banned"].append(member)
    elif action == "kick":
        if member in group.get("members", []): group["members"].remove(member)
        if member in group.get("subscribers", []): group["subscribers"].remove(member)
    elif action == "promote" and member not in group["admins"]: group["admins"].append(member)
    elif action == "transfer": group["owner"] = member
    save_db(db)
    return "Готово"

def edit_message(chat_name, msg_index, new_text, sender):
    db = load_db()
    if chat_name in db["history"]:
        history = db["history"][chat_name]
        if 0 <= msg_index < len(history):
            msg = history[msg_index]
            if msg["sender"] == sender and not msg["text"].startswith("📎"):
                msg["text"] = new_text
                save_db(db)
                return True
    return False

def delete_message(chat_name, msg_index, sender, delete_for_all=True):
    db = load_db()
    if chat_name in db["history"]:
        history = db["history"][chat_name]
        if 0 <= msg_index < len(history):
            if delete_for_all:
                if history[msg_index]["sender"] == sender:
                    history.pop(msg_index)
                    save_db(db)
                    return True
            else:
                if "hidden_for" not in history[msg_index]:
                    history[msg_index]["hidden_for"] = []
                if sender not in history[msg_index]["hidden_for"]:
                    history[msg_index]["hidden_for"].append(sender)
                save_db(db)
                return True
    return False
