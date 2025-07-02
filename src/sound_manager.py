# NongGameTyping/src/sound_manager.py
import pygame
import os
from .data_manager import DataManager

class SoundManager:
    """
    จัดการการโหลดและเล่นเสียงทั้งหมดในเกม
    ตรวจสอบไฟล์ก่อนโหลด ถ้าไม่มีไฟล์จะข้ามไปและแสดงคำเตือน
    """
    def __init__(self):
        self.sounds = {}
        self.bgm_path = None
        
        # Initialize data manager for asset paths
        self.data_manager = DataManager()
        
        # Load volume settings
        settings = self.data_manager.get_settings()
        self.sound_volume = settings.get('sound_volume', 0.5)
        self.music_volume = settings.get('music_volume', 0.3)
        
        try:
            pygame.mixer.init()
            print("Pygame mixer initialized successfully.")

            # --- โหลด Sound Effects (SFX) ---
            sfx_to_load = {
                'typing': 'typing.wav',
                'success': 'success.mp3',
                'error': 'error.mp3',
                'gacha_start': 'gacha_start.wav',
                'gacha_result': 'gacha_result.wav',
                'button': 'button.wav',
                'harvest': 'harvest.wav',
                'button_hover': 'button_hover.wav',
                'gacha_bgm': 'gacha_bgm.mp3',
            }

            for name, filename in sfx_to_load.items():
                path = self.data_manager.get_assets_path("sounds", filename)
                # ตรวจสอบว่าไฟล์มีอยู่จริงหรือไม่ ก่อนที่จะโหลด
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                else:
                    print(f"Warning: SFX file not found, skipping: {path}")

            # --- เตรียม Background Music (BGM) ---
            bgm_file = self.data_manager.get_assets_path("sounds", "bgm.mp3")
            # ตรวจสอบว่าไฟล์มีอยู่จริงหรือไม่
            if os.path.exists(bgm_file):
                self.bgm_path = bgm_file
            else:
                print(f"Warning: BGM file not found, skipping: {bgm_file}")

        except Exception as e:
            print(f"An error occurred during SoundManager initialization: {e}")
            # หากเกิดปัญหาในการ init mixer ให้ปิดการใช้งานเสียงทั้งหมด
            self.sounds = {}
            self.bgm_path = None

    def update_volumes(self):
        """อัปเดตระดับเสียงจาก DataManager"""
        settings = self.data_manager.get_settings()
        self.sound_volume = settings.get('sound_volume', 0.5)
        self.music_volume = settings.get('music_volume', 0.3)
        
        # อัปเดตระดับเสียงของ BGM ที่กำลังเล่นอยู่
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.music_volume)

    def play_bgm(self, volume=None):
        """เล่นดนตรีพื้นหลังแบบวนลูป"""
        if volume is None:
            volume = self.music_volume
        # self.bgm_path จะเป็น None ถ้าหาไฟล์ไม่เจอตั้งแต่แรก
        if self.bgm_path:
            try:
                pygame.mixer.music.load(self.bgm_path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass

    def play_sfx(self, name, volume=None):
        """เล่นเอฟเฟกต์เสียง"""
        if volume is None:
            volume = self.sound_volume
        # โค้ดส่วนนี้ทำงานได้ดีอยู่แล้ว เพราะมันเช็คว่า 'name' อยู่ใน self.sounds หรือไม่
        if name in self.sounds:
            try:
                self.sounds[name].set_volume(volume)
                self.sounds[name].play()
            except pygame.error:
                pass

    def play_gacha_bgm(self, volume=None):
        """เล่น BGM สำหรับหน้ากาชา"""
        if volume is None:
            volume = self.music_volume
        gacha_bgm_file = self.data_manager.get_assets_path("sounds", "gacha_bgm.mp3")
        if os.path.exists(gacha_bgm_file):
            try:
                pygame.mixer.music.load(gacha_bgm_file)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass