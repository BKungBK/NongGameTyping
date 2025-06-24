# NongGameTyping/src/word_manager.py
import json
import random
import os

class WordManager:
    """จัดการการโหลดและสุ่มคำศัพท์จากไฟล์ JSON"""
    def __init__(self, words_file_path):
        self.words = self.load_words(words_file_path)
        self.current_word = self.get_new_word()

    def load_words(self, file_path):
        """โหลดคำศัพท์จากไฟล์ JSON"""
        try:
            # สร้าง path ที่ถูกต้องโดยอิงจากตำแหน่งของไฟล์นี้
            full_path = os.path.join(os.path.dirname(__file__), file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading words file: {e}")
            # ถ้าหาไฟล์ไม่เจอ ให้ใช้คำศัพท์สำรอง
            return ["error", "file", "not", "found"]

    def get_new_word(self):
        """สุ่มคำใหม่จากลิสต์"""
        self.current_word = random.choice(self.words)
        return self.current_word