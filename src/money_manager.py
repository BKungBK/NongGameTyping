# NongGameTyping/src/money_manager.py
from .data_manager import DataManager

class MoneyManager:
    """จัดการเงินในเกม"""
    def __init__(self):
        self.data_manager = DataManager()
        # โหลดข้อมูลเงินจาก DataManager
        settings = self.data_manager.get_settings()
        self.coins = settings.get('coins', 1000)  # เริ่มต้นด้วย 1000 coin ถ้าไม่มีข้อมูล

    def add_coins(self, amount):
        """เพิ่มเงิน"""
        if amount > 0:
            self.coins += amount
            self._save_coins()

    def spend_coins(self, amount):
        """ใช้เงิน (ถ้ามีพอ)"""
        if self.coins >= amount:
            self.coins -= amount
            self._save_coins()
            return True
        return False

    def get_coins(self):
        """รับจำนวนเงินปัจจุบัน"""
        return self.coins

    def get_display_value(self):
        """รับค่าสำหรับแสดงผล"""
        return f"{self.coins}"

    def _save_coins(self):
        """บันทึกข้อมูลเงินลง DataManager"""
        settings = self.data_manager.get_settings()
        settings['coins'] = self.coins
        self.data_manager.update_settings(settings)