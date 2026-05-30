import os
import sys
import shutil
from pathlib import Path
from tkinter import messagebox

import pygame
try:
    pygame.mixer.init()
except Exception as e:
    print(f"Предупреждение: Не удалось инициализировать аудио-драйвер: {e}")

class PulsarMediaPlayer:
    current_playing_file = None
    is_paused = False

    @classmethod
    def play_audio(cls, file_path):
        """Воспроизведение или продолжение аудио треков (MP3/WAV)"""
        if not os.path.exists(file_path):
            messagebox.showerror("Ошибка", "Аудиофайл не найден на компьютере!")
            return
        
        try:
            clean_path = os.path.normpath(file_path)
            
            # Если этот же файл стоял на паузе — снимаем с паузы
            if cls.current_playing_file == clean_path and cls.is_paused:
                pygame.mixer.music.unpause()
                cls.is_paused = False
                return "resumed"
            
            # Если включаем новый файл — останавливаем старый и загружаем заново
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            
            pygame.mixer.music.load(clean_path)
            pygame.mixer.music.play()
            cls.current_playing_file = clean_path
            cls.is_paused = False
            return "started"
        except Exception as e:
            messagebox.showerror("Ошибка звука", f"Не удалось воспроизвести файл: {e}")
            return "error"

    @classmethod
    def pause_audio(cls):
        """Ставит текущее аудио на паузу"""
        try:
            if pygame.mixer.music.get_busy() and not cls.is_paused:
                pygame.mixer.music.pause()
                cls.is_paused = True
                return True
        except:
            pass
        return False

    @staticmethod
    def watch_video(file_path):
        from pulsar_video_player import PulsarVideoPlayer
        PulsarVideoPlayer(file_path)

    @staticmethod
    def download_media(source_path):
        if not os.path.exists(source_path):
            messagebox.showerror("Ошибка", "Файл не найден!")
            return
        try:
            downloads_dir = Path.home() / "Downloads"
            downloads_dir.mkdir(parents=True, exist_ok=True)
            original_name = os.path.basename(source_path)
            destination_path = downloads_dir / original_name
            
            with open(source_path, "rb") as src_file:
                with open(destination_path, "wb") as dest_file:
                    dest_file.write(src_file.read())
            messagebox.showinfo("Успех", f"Файл сохранен в Загрузки!\nИмя: {original_name}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось скачать файл: {e}")
