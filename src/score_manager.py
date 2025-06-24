# NongGameTyping/src/score_manager.py
class ScoreManager:
    """จัดการคะแนนและคอมโบ"""
    def __init__(self):
        self.score = 0
        self.combo = 0

    def add_score(self, base_points=10):
        """เพิ่มคะแนน โดยมีคะแนนพิเศษจากคอมโบ"""
        combo_bonus = self.combo * 2  # ให้โบนัสตามค่าคอมโบ
        self.score += base_points + combo_bonus
        self.increment_combo()

    def increment_combo(self):
        """เพิ่มคอมโบ"""
        self.combo += 1

    def reset_combo(self):
        """รีเซ็ตคอมโบเป็น 0"""
        self.combo = 0

    def get_display_values(self):
        """ส่งค่าคะแนนและคอมโบสำหรับแสดงผล"""
        return f"Score: {self.score}", f"Combo: {self.combo}x"