# NongGameTyping/src/word_manager.py
import random
from .data_manager import DataManager

class WordManager:
    """จัดการการโหลดและสุ่มคำศัพท์จาก DataManager"""
    def __init__(self):
        self.data_manager = DataManager()
        self.words = self.data_manager.get_words()
        self.current_word = self.get_new_word()

    def get_new_word(self):
        """สุ่มคำใหม่จากลิสต์"""
        self.current_word = self.data_manager.get_random_word()
        return self.current_word