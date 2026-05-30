import customtkinter as ctk
from PIL import Image
import os
import threading
import time
import pygame

# Универсальный импорт VideoFileClip, адаптированный под старые и новые версии moviepy
try:
    from moviepy import VideoFileClip
except ImportError:
    from moviepy.editor import VideoFileClip

# Инициализация звукового движка pygame
pygame.mixer.init()

class PulsarVideoPlayer(ctk.CTkToplevel):
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.title(f"Pulsar Pro Player - {os.path.basename(video_path)}")
        self.geometry("800x650")
        self.attributes("-topmost", True)
        
        self.is_playing = False
        self.playback_speed = 1.0
        self.volume_level = 0.5
        self.current_time = 0.0
        
        # Загружаем видео через moviepy
        try:
            self.clip = VideoFileClip(self.video_path)
            self.fps = self.clip.fps if self.clip.fps else 24.0
            self.duration = self.clip.duration
            self.has_audio = self.clip.audio is not None
        except Exception as e:
            print(f"Ошибка загрузки видео через moviepy: {e}")
            self.destroy()
            return

        # Экспорт звуковой дорожки
        if self.has_audio:
            try:
                self.temp_audio = f"temp_{int(time.time())}.wav"
                self.clip.audio.write_audiofile(self.temp_audio, logger=None)
                pygame.mixer.music.load(self.temp_audio)
                pygame.mixer.music.set_volume(self.volume_level)
            except Exception as ae:
                print(f"Не удалось настроить аудио: {ae}")
                self.has_audio = False

        # Экран видео
        self.video_label = ctk.CTkLabel(self, text="Загрузка медиапотока...", fg_color="black")
        self.video_label.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Панель управления
        control_frame = ctk.CTkFrame(self, height=120)
        control_frame.pack(fill="x", side="bottom", padx=15, pady=15)
        
        btn_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10, padx=10)
        
        self.btn_play = ctk.CTkButton(btn_frame, text="▶ Воспроизвести", width=120, fg_color="#34C759", command=self.start_video)
        self.btn_play.pack(side="left", padx=5)
        
        btn_pause = ctk.CTkButton(btn_frame, text="⏸ Пауза", width=100, fg_color="#FF9500", text_color="black", command=self.pause_video)
        btn_pause.pack(side="left", padx=5)
        
        from pulsar_media_player import PulsarMediaPlayer
        btn_dl = ctk.CTkButton(btn_frame, text="📥 Скачать в Загрузки", fg_color="#007AFF", command=lambda: PulsarMediaPlayer.download_media(self.video_path))
        btn_dl.pack(side="right", padx=5)
        
        # Слайдеры управления медиапотоком
        sliders_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        sliders_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(sliders_frame, text="🔊 Громкость:", font=("Arial", 12)).pack(side="left", padx=(10, 5))
        self.vol_slider = ctk.CTkSlider(sliders_frame, from_=0.0, to=1.0, width=150, command=self.change_volume)
        self.vol_slider.set(self.volume_level)
        self.vol_slider.pack(side="left", padx=5)
        
        ctk.CTkLabel(sliders_frame, text="⚡ Скорость:", font=("Arial", 12)).pack(side="left", padx=(30, 5))
        self.speed_slider = ctk.CTkSlider(sliders_frame, from_=0.5, to=2.0, width=150, command=self.change_speed)
        self.speed_slider.set(self.playback_speed)
        self.speed_slider.pack(side="left", padx=5)
        
        self.lbl_speed_val = ctk.CTkLabel(sliders_frame, text="1.0x", font=("Arial", 12, "bold"), text_color="#00A2FF")
        self.lbl_speed_val.pack(side="left", padx=5)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.start_video()

    def start_video(self):
        if self.is_playing: return
        self.is_playing = True
        
        if self.has_audio:
            try: pygame.mixer.music.play(start=self.current_time)
            except: pass
                
        threading.Thread(target=self.play_loop, daemon=True).start()

    def pause_video(self):
        self.is_playing = False
        if self.has_audio:
            pygame.mixer.music.pause()

    def change_volume(self, value):
        self.volume_level = float(value)
        if self.has_audio:
            pygame.mixer.music.set_volume(self.volume_level)

    def change_speed(self, value):
        self.playback_speed = round(float(value), 1)
        self.lbl_speed_val.configure(text=f"{self.playback_speed}x")
        if self.has_audio and self.is_playing:
            pygame.mixer.music.stop()
            pygame.mixer.music.play(start=self.current_time)

    def play_loop(self):
        start_sys_time = time.time() - (self.current_time / self.playback_speed)
        
        while self.is_playing:
            self.current_time = (time.time() - start_sys_time) * self.playback_speed
            
            if self.current_time >= self.duration:
                self.current_time = 0.0
                start_sys_time = time.time()
                if self.has_audio:
                    try: pygame.mixer.music.play()
                    except: pass
            
            try:
                frame = self.clip.get_frame(self.current_time)
                img = Image.fromarray(frame)
                
                w = self.video_label.winfo_width()
                h = self.video_label.winfo_height()
                if w < 10 or h < 10: w, h = 760, 420
                
                img = img.resize((w, h), Image.Resampling.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(w, h))
                
                self.video_label.configure(image=ctk_img, text="")
            except:
                break
                
            time.sleep(max(0.001, (1.0 / self.fps) / self.playback_speed))

    def on_close(self):
        self.is_playing = False
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        if hasattr(self, 'clip'):
            self.clip.close()
        if hasattr(self, 'temp_audio') and os.path.exists(self.temp_audio):
            try: os.remove(self.temp_audio)
            except: pass
        self.destroy()
