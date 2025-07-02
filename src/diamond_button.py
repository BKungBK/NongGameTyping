import pygame
import math
import random

WHITE = (255, 255, 255)

class Particle:
    """
    อนุภาคสำหรับเอฟเฟกต์ particle ด้านหลังปุ่ม DiamondButton
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.alpha = 255
        self.size = random.uniform(1, 3)
        self.color = random.choice([(144, 238, 144), (173, 255, 173), (200, 255, 200), WHITE])
        self.life = random.uniform(0.5, 2.0)
        self.max_life = self.life

    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.life -= dt
        self.alpha = max(0, int(255 * (self.life / self.max_life)))
        self.vx *= 0.98
        self.vy *= 0.98
        return self.life > 0

    def draw(self, screen):
        if self.alpha > 0:
            particle_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            color_with_alpha = (*self.color[:3], self.alpha)
            pygame.draw.circle(particle_surface, color_with_alpha, (int(self.size), int(self.size)), int(self.size))
            screen.blit(particle_surface, (self.x - self.size, self.y - self.size))

class DiamondButton:
    """
    ปุ่ม DiamondButton แบบโปร่งใส มีขอบหลายชั้นและเอฟเฟกต์ particle
    สามารถใช้ icon ได้ (รองรับขนาด icon แบบกำหนดเอง)
    """
    def __init__(self, x, y, size, icon_surface=None, sound_manager=None):
        self.x = x
        self.y = y
        self.size = size
        self.icon = icon_surface.copy() if icon_surface else None
        self.is_hovered = False
        self.is_pressed = False
        self.rotation_angle = 0
        self.inner_rotation_angle = 0
        self.bounce_time = 0
        self.bounce_amplitude = 4
        self.bounce_frequency = 0.5
        self.rotation_speed = 1
        self.inner_rotation_speed = 0.75
        self.particles = []
        self.particle_spawn_timer = 0
        self.particle_spawn_rate = 0.15
        self.outer_points = self._calculate_diamond_points(x, y, size)
        self.middle_points = self._calculate_diamond_points(x, y, size - 15)
        self.inner_points = self._calculate_diamond_points(x, y, size - 30)
        self.sound_manager = sound_manager
        self._was_hovered = False

    def _calculate_diamond_points(self, center_x, center_y, size, rotation=0):
        half_size = size // 2
        base_points = [
            (0, -half_size),
            (half_size, 0),
            (0, half_size),
            (-half_size, 0)
        ]
        if rotation != 0:
            cos_r = math.cos(math.radians(rotation))
            sin_r = math.sin(math.radians(rotation))
            rotated_points = []
            for px, py in base_points:
                new_x = px * cos_r - py * sin_r
                new_y = px * sin_r + py * cos_r
                rotated_points.append((new_x, new_y))
            base_points = rotated_points
        points = [(center_x + px, center_y + py) for px, py in base_points]
        return points

    def spawn_particles(self, dt):
        if not self.is_hovered:
            return
        self.particle_spawn_timer += dt
        if self.particle_spawn_timer >= self.particle_spawn_rate:
            self.particle_spawn_timer = 0
            for _ in range(random.randint(2, 4)):
                offset_x = random.uniform(-self.size//3, self.size//3)
                offset_y = random.uniform(-self.size//3, self.size//3)
                particle = Particle(self.x + offset_x, self.y + offset_y)
                self.particles.append(particle)

    def update_animation(self, dt):
        if self.is_hovered:
            self.rotation_angle += self.rotation_speed * dt * 60
            if self.rotation_angle >= 360:
                self.rotation_angle -= 360
            self.inner_rotation_angle -= self.inner_rotation_speed * dt * 60
            if self.inner_rotation_angle <= -360:
                self.inner_rotation_angle += 360
            self.bounce_time += dt
        else:
            self.rotation_angle *= 0.95
            self.inner_rotation_angle *= 0.95
            if abs(self.rotation_angle) < 0.1:
                self.rotation_angle = 0
            if abs(self.inner_rotation_angle) < 0.1:
                self.inner_rotation_angle = 0
            self.bounce_time = 0
        self.outer_points = self._calculate_diamond_points(self.x, self.y, self.size, self.rotation_angle)
        self.middle_points = self._calculate_diamond_points(self.x, self.y, self.size - 15, self.rotation_angle)
        self.inner_points = self._calculate_diamond_points(self.x, self.y, self.size - 30, self.inner_rotation_angle)
        self.spawn_particles(dt)
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, screen):
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)
        # Draw outer diamond (ขาวสุด)
        pygame.draw.polygon(screen, WHITE, self.outer_points, 3)
        # Draw middle diamond (สีอ่อนลง)
        MIDDLE_COLOR = (200, 200, 200)
        pygame.draw.polygon(screen, MIDDLE_COLOR, self.middle_points, 2)
        # Draw inner diamond (สีอ่อนลงอีก)
        INNER_COLOR = (150, 150, 150)
        pygame.draw.polygon(screen, INNER_COLOR, self.inner_points, 2)
        # Draw icon
        if self.icon:
            if self.is_hovered:
                bounce_offset = math.sin(self.bounce_time * self.bounce_frequency * 2 * math.pi) * self.bounce_amplitude
            else:
                bounce_offset = 0
            icon_y = self.y + bounce_offset
            
            # Calculate appropriate icon size (about 40% of button size)
            icon_size = int(self.size * 0.4)
            
            # Scale the icon to fit properly
            scaled_icon = pygame.transform.smoothscale(self.icon, (icon_size, icon_size))
            scaled_rect = scaled_icon.get_rect(center=(self.x, icon_y))
            screen.blit(scaled_icon, scaled_rect)

    def is_point_inside(self, point):
        x, y = point
        dx = abs(x - self.x)
        dy = abs(y - self.y)
        return (dx + dy) <= (self.size // 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            hovered = self.is_point_inside(event.pos)
            if hovered and not self.is_hovered:
                if self.sound_manager:
                    self.sound_manager.play_sfx('button_hover')
            self.is_hovered = hovered
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_point_inside(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_pressed = False
        return False 