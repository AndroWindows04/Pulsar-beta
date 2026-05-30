import os
import time
import threading
import sounddevice as sd
from scipy.io.wavfile import write

class PulsarVoiceRecorder:
    def __init__(self):
        self.is_recording = False
        self.recording_data = None
        self.fs = 44100  # Частота дискретизации звука
        self.duration = 30  # Максимальное время записи (30 секунд)

    def start_recording(self):
        """Запуск записи аудио в фоновом режиме"""
        self.is_recording = True
        # Запуск записи входящего потока данных
        self.recording_data = sd.rec(int(self.duration * self.fs), samplerate=self.fs, channels=1, dtype='int16')

    def stop_recording(self):
        """Остановка записи микрофона и сохранение аудио на диск"""
        if not self.is_recording:
            return None
            
        self.is_recording = False
        sd.stop()
        
        # Создаем папку под кэш мессенджера, если её нет
        os.makedirs("pulsar_media", exist_ok=True)
        voice_path = f"pulsar_media/voice_msg_{int(time.time())}.wav"
        
        # Записываем аудиофайл
        write(voice_path, self.fs, self.recording_data)
        return voice_path
