# NongGameTyping/src/combo_manager.py
class ComboManager:
    """จัดการคอมโบ (สำหรับคูณเปอร์เซ็นต์การโต)"""
    def __init__(self):
        self.combo = 0

    def increment_combo(self):
        """เพิ่มคอมโบ"""
        self.combo += 1

    def reset_combo(self):
        """รีเซ็ตคอมโบเป็น 0"""
        self.combo = 0

    def get_combo_multiplier(self):
        """คืนค่าตัวคูณเปอร์เซ็นต์การโตตามคอมโบ (เช่น 1.0 + 0.1*combo)"""
        return 1.0 + 0.1 * self.combo

    def get_display_value(self):
        """ส่งค่าคอมโบสำหรับแสดงผล"""
        return f"Combo {self.combo}x" 