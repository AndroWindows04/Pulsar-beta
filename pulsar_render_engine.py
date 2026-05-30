import customtkinter as ctk
import os
from pulsar_media_player import PulsarMediaPlayer as player

class PulsarRenderEngine:
    @staticmethod
    def get_avatar(path, size=40):
        if path and os.path.exists(path):
            try:
                from PIL import Image
                img = Image.open(path)
                return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
            except: pass
        return None

    @classmethod
    def draw_bubble(cls, scroll_container, sender, text, is_own, msg_index, app_context):
        row = ctk.CTkFrame(scroll_container, fg_color="transparent")
        row.pack(fill="x", pady=4)
        
        bubble = ctk.CTkFrame(row, fg_color="#007AFF" if is_own else "#3A3A3C", corner_radius=12)
        bubble.pack(side="right" if is_own else "left", padx=10)
        
        display_sender = text if is_own else f"{sender}:\n{text}"
        is_media = text.startswith("📎")

        def on_bubble_right_click(event):
            if is_own:
                app_context.open_message_actions(msg_index, text, is_media)

        content_frame = ctk.CTkFrame(bubble, fg_color="transparent")
        content_frame.pack(padx=10, pady=5)
        
        if is_media:
            clean_path = text.replace("📎 ", "").strip()
            file_name = os.path.basename(clean_path)
            ext = file_name.split(".")[-1].lower()
            
            # --- ГИС (Голосовые сообщения) ---
            if "voice_msg" in file_name:
                lbl = ctk.CTkLabel(content_frame, text=f"🎙️ {sender}: Голосовое сообщение", font=("Arial", 13, "italic"))
                lbl.pack(pady=4)
                
                bf = ctk.CTkFrame(content_frame, fg_color="transparent")
                bf.pack(pady=2)
                
                ctk.CTkButton(bf, text="▶ Слушать", width=80, height=22, fg_color="#34C759", 
                               command=lambda: player.play_audio(clean_path)).pack(side="left", padx=2)
                ctk.CTkButton(bf, text="⏸ Пауза", width=60, height=22, fg_color="#FF9500", text_color="black", 
                               command=player.pause_audio).pack(side="left", padx=2)
                
                ctk.CTkButton(content_frame, text="📥 Скачать", width=144, height=22, fg_color="#2C2C2E", 
                               command=lambda: player.download_media(clean_path)).pack(pady=2)
                
            # --- Музыка ---
            elif ext in ["mp3", "wav"]:
                lbl = ctk.CTkLabel(content_frame, text=f"🎵 {file_name}", font=("Arial", 13))
                lbl.pack(pady=4)
                
                bf = ctk.CTkFrame(content_frame, fg_color="transparent")
                bf.pack(pady=2)
                
                ctk.CTkButton(bf, text="▶ Играть", width=80, height=22, fg_color="#4CD964", text_color="white", 
                               command=lambda: player.play_audio(clean_path)).pack(side="left", padx=2)
                ctk.CTkButton(bf, text="⏸ Пауза", width=60, height=22, fg_color="#FF9500", text_color="black", 
                               command=player.pause_audio).pack(side="left", padx=2)
                
                ctk.CTkButton(content_frame, text="📥 Скачать файл", width=144, height=22, fg_color="#2C2C2E", 
                               command=lambda: player.download_media(clean_path)).pack(pady=2)
                
            # --- Видео ---
            elif ext in ["mp4", "avi", "mkv", "mov"]:
                lbl = ctk.CTkLabel(content_frame, text=f"🎥 Видео: {file_name}", font=("Arial", 13, "bold"))
                lbl.pack(pady=4)
                
                ctk.CTkButton(content_frame, text="🎬 Открыть в Pulsar Player", width=160, height=22, fg_color="#5856D6", 
                               command=lambda: player.watch_video(clean_path)).pack(pady=2)
                ctk.CTkButton(content_frame, text="📥 Скачать в Загрузки", width=160, height=22, fg_color="#2C2C2E", 
                               command=lambda: player.download_media(clean_path)).pack(pady=2)
            else:
                ctk.CTkLabel(content_frame, text=text, font=("Arial", 14)).pack()
        else:
            lbl = ctk.CTkLabel(content_frame, text=display_sender, font=("Arial", 14), justify="left", wraplength=450)
            lbl.pack()

        if is_own:
            content_frame.bind("<Button-3>", on_bubble_right_click)
            bubble.bind("<Button-3>", on_bubble_right_click)
            row.bind("<Button-3>", on_bubble_right_click)
            for child in content_frame.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    child.bind("<Button-3>", on_bubble_right_click)
