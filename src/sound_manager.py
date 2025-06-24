# NongGameTyping/src/sound_manager.py
import pygame
import os

class SoundManager:
    """
    จัดการการโหลดและเล่นเสียงทั้งหมดในเกม
    ตรวจสอบไฟล์ก่อนโหลด ถ้าไม่มีไฟล์จะข้ามไปและแสดงคำเตือน
    """
    def __init__(self):
        self.sounds = {}
        self.bgm_path = None
        
        try:
            pygame.mixer.init()
            print("Pygame mixer initialized successfully.")

            # --- โหลด Sound Effects (SFX) ---
            sfx_to_load = {
                'typing': 'typing.wav',
                'success': 'success.mp3',
                'error': 'error.mp3'
            }

            for name, filename in sfx_to_load.items():
                path = os.path.join('assets', 'sounds', filename)
                # ตรวจสอบว่าไฟล์มีอยู่จริงหรือไม่ ก่อนที่จะโหลด
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                else:
                    print(f"Warning: SFX file not found, skipping: {path}")

            # --- เตรียม Background Music (BGM) ---
            bgm_file = os.path.join('assets', 'sounds', 'bgm.mp3')
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


    def play_bgm(self, volume=0.3):
        """เล่นดนตรีพื้นหลังแบบวนลูป"""
        # self.bgm_path จะเป็น None ถ้าหาไฟล์ไม่เจอตั้งแต่แรก
        if self.bgm_path:
            try:
                pygame.mixer.music.load(self.bgm_path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass


    def play_sfx(self, name, volume=0.5):
        """เล่นเอฟเฟกต์เสียง"""
        # โค้ดส่วนนี้ทำงานได้ดีอยู่แล้ว เพราะมันเช็คว่า 'name' อยู่ใน self.sounds หรือไม่
        if name in self.sounds:
            try:
                self.sounds[name].set_volume(volume)
                self.sounds[name].play()
            except pygame.error:
                pass