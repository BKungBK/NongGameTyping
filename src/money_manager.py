# NongGameTyping/src/money_manager.py
class MoneyManager:
    """จัดการเงินในเกม"""
    def __init__(self):
        self.coins = 0

    def add_coins(self, amount):
        """เพิ่มเงิน"""
        if amount > 0:
            self.coins += amount

    def get_display_value(self):
        return f"{self.coins}"