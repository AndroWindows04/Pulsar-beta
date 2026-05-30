from tkinter import filedialog

def choose_media_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Медиафайлы", "*.mp3 *.wav *.png *.jpg *.jpeg *.gif")]
    )
    if not file_path: return None
    file_name = file_path.split("/")[-1]
    ext = file_name.split(".")[-1].lower()
    if ext in ["mp3", "wav"]:
        return {"type": "audio", "name": f"🎵 Аудио: {file_name}"}
    return {"type": "image", "name": f"🖼️ Фото: {file_name}"}

def choose_avatar():
    return filedialog.askopenfilename(
        filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp")]
    )
