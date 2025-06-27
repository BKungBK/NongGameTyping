import math
import random
import pygame

class FireworkParticle:
    def __init__(self, x, y, angle, speed, color, scale=1.0, lifetime=1.0, gravity=200, friction=0.98):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.color = color
        self.scale = scale
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.friction = friction
        self.alive = True

    def update(self, dt):
        if not self.alive:
            return
        self.vel.y += self.gravity * dt
        self.pos += self.vel * dt
        self.vel *= self.friction
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surf):
        if not self.alive:
            return
        fade = max(0, (self.lifetime / self.max_lifetime) ** 1.8)
        alpha = int(255 * fade)
        radius = max(1, int(3 * self.scale * fade))
        color = (*self.color[:3], alpha)
        pygame.draw.circle(surf, color, (int(self.pos.x), int(self.pos.y)), radius)

class FireworkExplosion:
    def __init__(self):
        self.particles = []

    def explode(self, x, y, base_color=None, count=40):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 180)
            scale = random.uniform(0.8, 1.5)
            lifetime = random.uniform(1.0, 1.8)

            # ใช้สีสุ่มแบบไล่โทน
            if base_color:
                r = min(255, base_color[0] + random.randint(-30, 30))
                g = min(255, base_color[1] + random.randint(-30, 30))
                b = min(255, base_color[2] + random.randint(-30, 30))
            else:
                r, g, b = [random.randint(128, 255) for _ in range(3)]

            color = (r, g, b)
            self.particles.append(FireworkParticle(x, y, angle, speed, color, scale, lifetime))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update(dt)

    def draw(self, surf):
        for p in self.particles:
            p.draw(surf)
