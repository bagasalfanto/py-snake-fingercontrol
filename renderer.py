import time

import cv2
import numpy as np
import pygame

from config import (
    CAM_H,
    CAM_W,
    CELL_SIZE,
    COLOR_BG,
    COLOR_CAM_BORDER,
    COLOR_FOOD,
    COLOR_FOOD_SHINE,
    COLOR_GRID,
    COLOR_OBSTACLE,
    COLOR_POWERUP,
    COLOR_SCORE,
    COLOR_SHIELD,
    COLOR_SNAKE_BODY,
    COLOR_SNAKE_HEAD,
    COLOR_SNAKE_SHINE,
    COLOR_TEXT,
    COLOR_WARNING,
    DOWN,
    ENABLE_DIFFICULTY_SELECT,
    ENABLE_GESTURE_CONTROL,
    ENABLE_GESTURE_POWER_SKILL,
    ENABLE_HIGH_SCORE,
    ENABLE_KEYBOARD_CONTROL,
    ENABLE_PAUSE,
    ENABLE_RESET,
    LEFT,
    RIGHT,
    SCREEN_H,
    SCREEN_W,
    UP,
)
from entities import PowerUp


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.f_large = pygame.font.SysFont("Consolas", 48, bold=True)
        self.f_medium = pygame.font.SysFont("Consolas", 28, bold=True)
        self.f_small = pygame.font.SysFont("Consolas", 18)
        self.f_tiny = pygame.font.SysFont("Consolas", 14)

    def draw_grid(self, level=1):
        tint = min(35, (level - 1) * 4)
        self.screen.fill((COLOR_BG[0] + tint, COLOR_BG[1], COLOR_BG[2] + tint))
        for x in range(0, SCREEN_W, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (SCREEN_W, y))

    def draw_snake(self, snake):
        for i, (cx, cy) in enumerate(snake.body):
            r = pygame.Rect(cx*CELL_SIZE+1, cy*CELL_SIZE+1, CELL_SIZE-2, CELL_SIZE-2)
            if i == 0:
                pygame.draw.rect(self.screen, COLOR_SNAKE_HEAD, r, border_radius=4)
                pygame.draw.rect(self.screen, COLOR_SNAKE_SHINE,
                                 pygame.Rect(r.x+2, r.y+2, 5, 5), border_radius=2)
                self._draw_eyes(cx, cy, snake.direction)
            else:
                fade = max(0.4, 1.0 - i * 0.015)
                c = tuple(int(v * fade) for v in COLOR_SNAKE_BODY)
                pygame.draw.rect(self.screen, c, r, border_radius=3)

    def _draw_eyes(self, cx, cy, direction):
        bx, by = cx * CELL_SIZE, cy * CELL_SIZE
        half = CELL_SIZE // 2
        offsets = {
            RIGHT: [(CELL_SIZE-5, half-3), (CELL_SIZE-5, half+3)],
            LEFT: [(5, half-3), (5, half+3)],
            UP: [(half-3, 5), (half+3, 5)],
            DOWN: [(half-3, CELL_SIZE-5), (half+3, CELL_SIZE-5)],
        }
        for ox, oy in offsets.get(direction, []):
            pygame.draw.circle(self.screen, (20, 20, 20), (bx+ox, by+oy), 2)

    def draw_food(self, food):
        fx, fy = food.pos
        size = int(CELL_SIZE * 0.8 + food.pulse * CELL_SIZE * 0.2)
        off = (CELL_SIZE - size) // 2
        r = pygame.Rect(fx*CELL_SIZE+off, fy*CELL_SIZE+off, size, size)
        pygame.draw.rect(self.screen, COLOR_FOOD, r, border_radius=size//3)
        pygame.draw.rect(self.screen, COLOR_FOOD_SHINE,
                         pygame.Rect(r.x+2, r.y+2, 4, 4), border_radius=2)

    def draw_powerup(self, powerup):
        if powerup is None:
            return
        px, py = powerup.pos
        size = int(CELL_SIZE * 0.85 + powerup.pulse * CELL_SIZE * 0.15)
        off = (CELL_SIZE - size) // 2
        r = pygame.Rect(px*CELL_SIZE+off, py*CELL_SIZE+off, size, size)
        color = PowerUp.COLORS.get(powerup.kind, COLOR_POWERUP)
        pygame.draw.rect(self.screen, color, r, border_radius=5)
        label = PowerUp.LABELS.get(powerup.kind, "?")
        text = self.f_tiny.render(label, True, (10, 10, 20))
        self.screen.blit(text, (r.centerx - text.get_width()//2,
                                r.centery - text.get_height()//2))

    def draw_obstacles(self, obstacles):
        for ox, oy in obstacles:
            r = pygame.Rect(ox*CELL_SIZE+2, oy*CELL_SIZE+2, CELL_SIZE-4, CELL_SIZE-4)
            pygame.draw.rect(self.screen, COLOR_OBSTACLE, r, border_radius=3)
            pygame.draw.rect(self.screen, (150, 150, 180), r, 1, border_radius=3)

    def draw_particles(self, particles):
        for p in particles:
            alpha = max(40, int(255 * p.life / p.max_life))
            surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*p.color, alpha), (4, 4), 4)
            self.screen.blit(surf, (int(p.x), int(p.y)))

    def draw_score(self, score, hi, level=1, difficulty="Normal"):
        self.screen.blit(
            self.f_medium.render(f"SCORE: {score:04d}", True, COLOR_SCORE), (10, 10))
        self.screen.blit(
            self.f_small.render(f"BEST:  {hi:04d}", True, (150, 200, 150)), (10, 44))
        self.screen.blit(
            self.f_small.render(f"LEVEL: {level}  {difficulty}", True, (170, 170, 210)), (10, 68))

    def draw_effects(self, effects, shield, gesture_label):
        x, y = 10, 92
        labels = []
        if shield:
            labels.append(("SHIELD", COLOR_SHIELD))
        for key, until in effects.items():
            remain = max(0, int(until - time.monotonic()))
            labels.append((f"{key.upper()} {remain}s", PowerUp.COLORS.get(key, COLOR_TEXT)))
        labels.append((f"GESTURE: {gesture_label}", (150, 180, 220)))
        for text, color in labels:
            surf = self.f_tiny.render(text, True, color)
            self.screen.blit(surf, (x, y))
            y += 18

    def draw_cam(self, frame_bgr):
        if frame_bgr is None:
            return
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        surf = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
        cx = SCREEN_W - CAM_W - 10
        cy = 10
        pygame.draw.rect(self.screen, COLOR_CAM_BORDER,
                         pygame.Rect(cx-2, cy-2, CAM_W+4, CAM_H+4), border_radius=4)
        self.screen.blit(surf, (cx, cy))
        self.screen.blit(
            self.f_tiny.render("WEBCAM", True, COLOR_CAM_BORDER),
            (cx, cy + CAM_H + 4))

    def draw_no_cam(self):
        r = pygame.Rect(SCREEN_W - CAM_W - 10, 10, CAM_W, CAM_H)
        pygame.draw.rect(self.screen, (30, 30, 40), r, border_radius=4)
        pygame.draw.rect(self.screen, (80, 80, 80), r, 1, border_radius=4)
        for i, (txt, col) in enumerate([
            ("Webcam tidak", COLOR_WARNING),
            ("tersedia!", COLOR_WARNING),
            ("Gunakan WASD", (120, 120, 120)),
        ]):
            self.screen.blit(self.f_tiny.render(txt, True, col),
                             (r.x+10, r.y+40+i*18))

    def draw_hint(self, has_cam):
        if has_cam and ENABLE_GESTURE_CONTROL:
            parts = ["Geser telunjuk: arah"]
            if ENABLE_PAUSE:
                parts.append("Telapak: pause")
            if ENABLE_RESET:
                parts.append("Kepal: restart")
            if ENABLE_GESTURE_POWER_SKILL:
                parts.append("2 jari: skill")
            hint = " | ".join(parts)
        elif ENABLE_KEYBOARD_CONTROL:
            hint = "WASD / Arrow Keys untuk kontrol keyboard"
        else:
            hint = "Kontrol input sedang dimatikan"
        self.screen.blit(self.f_tiny.render(hint, True, (80, 80, 100)),
                         (10, SCREEN_H - 20))

    def draw_menu(self, difficulty, scores, has_cam):
        self.draw_grid()
        cx = SCREEN_W // 2
        title = self.f_large.render("SNAKE FINGER CONTROL", True, COLOR_SCORE)
        self.screen.blit(title, (cx - title.get_width()//2, 95))
        lines = [("ENTER  Mulai Game", COLOR_TEXT)]
        if ENABLE_DIFFICULTY_SELECT:
            lines.append((f"TAB    Difficulty: {difficulty}", (170, 210, 255)))
        if ENABLE_KEYBOARD_CONTROL:
            lines.append(("WASD / Arrow Keys tetap aktif", (150, 150, 170)))
        if ENABLE_GESTURE_CONTROL:
            gesture_parts = []
            if ENABLE_PAUSE:
                gesture_parts.append("telapak pause")
            if ENABLE_RESET:
                gesture_parts.append("kepal restart")
            if ENABLE_GESTURE_POWER_SKILL:
                gesture_parts.append("2 jari skill")
            gesture_text = ", ".join(gesture_parts) if gesture_parts else "arah jari"
            lines.append((f"Gesture: {gesture_text}", (150, 150, 170)))
        if ENABLE_HIGH_SCORE:
            lines.append((
                f"Best Score: {scores['best_score']} | Best Level: {scores['best_level']}",
                COLOR_SCORE,
            ))
        if not has_cam:
            lines.append(("Webcam tidak tersedia, mode keyboard aktif", COLOR_WARNING))
        y = 210
        for text, color in lines:
            surf = self.f_small.render(text, True, color)
            self.screen.blit(surf, (cx - surf.get_width()//2, y))
            y += 36

    def draw_pause(self):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        self.screen.blit(ov, (0, 0))
        text = self.f_large.render("PAUSED", True, COLOR_WARNING)
        self.screen.blit(text, (SCREEN_W//2 - text.get_width()//2, 240))
        hint = self.f_small.render("SPACE / Telapak untuk lanjut", True, COLOR_TEXT)
        self.screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, 305))

    def draw_game_over(self, score, hi, level=1, scores=None):
        scores = scores or {"games_played": 0}
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        self.screen.blit(ov, (0, 0))
        bw, bh = 520, 260
        bx = (SCREEN_W - bw) // 2
        by = (SCREEN_H - bh) // 2
        br = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(self.screen, (20, 10, 10), br, border_radius=12)
        pygame.draw.rect(self.screen, (180, 30, 30), br, 2, border_radius=12)
        cx = SCREEN_W // 2

        def bc(surf, y):
            self.screen.blit(surf, (cx - surf.get_width()//2, y))

        bc(self.f_large.render("GAME OVER", True, (220, 50, 50)), by+20)
        bc(self.f_medium.render(f"Skor: {score}", True, COLOR_TEXT), by+90)
        bc(self.f_small.render(f"Level: {level} | Skor Tertinggi: {hi}", True, COLOR_SCORE), by+125)
        bc(self.f_tiny.render(f"Total main: {scores['games_played']}", True, (150, 150, 170)), by+152)
        bc(self.f_small.render("Tekan 'R' untuk Restart", True, (180, 180, 180)), by+175)
        bc(self.f_small.render("Tekan 'Q' untuk Keluar", True, (120, 120, 120)), by+205)
