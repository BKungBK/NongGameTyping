import pygame

class ShopScreen:
    def __init__(self, screen_width, screen_height, font, on_close_callback):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = font
        self.on_close = on_close_callback
        self.active = False
        # ปุ่มกลับ
        self.back_button_rect = pygame.Rect(
            self.screen_width // 2 - 80, self.screen_height - 120, 160, 60)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button_rect.collidepoint(event.pos):
                self.on_close()  # กลับไปเกมหลัก
                return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.on_close()
            return True
        return False

    def update(self, dt):
        pass  # รองรับอนาคต (animation ฯลฯ)

    def draw(self, surface):
        # วาดพื้นหลังโปร่งใส
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((20, 20, 40, 230))
        surface.blit(overlay, (0, 0))
        # วาดกล่องร้านค้า
        box_rect = pygame.Rect(self.screen_width//2-300, 100, 600, 400)
        pygame.draw.rect(surface, (40, 40, 60), box_rect, border_radius=18)
        pygame.draw.rect(surface, (100, 200, 255), box_rect, 4, border_radius=18)
        # ข้อความหัวข้อ
        title_surf = self.font.render("SHOP", True, (255,255,255))
        title_rect = title_surf.get_rect(center=(self.screen_width//2, 150))
        surface.blit(title_surf, title_rect)
        # ปุ่มกลับ
        pygame.draw.rect(surface, (100, 200, 255), self.back_button_rect, border_radius=14)
        back_surf = self.font.render("กลับ", True, (0,0,0))
        back_rect = back_surf.get_rect(center=self.back_button_rect.center)
        surface.blit(back_surf, back_rect)
        # (พื้นที่สำหรับของขายในอนาคต) 