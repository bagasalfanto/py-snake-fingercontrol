import os
import random
import sys
import time

import pygame

from config import (
    COLOR_FOOD,
    COLOR_POWERUP,
    COLOR_SHIELD,
    DIFFICULTIES,
    DOWN,
    ENABLE_ADVANCED_POWERUPS,
    ENABLE_DIFFICULTY_SELECT,
    ENABLE_GESTURE_CONTROL,
    ENABLE_GESTURE_POWER_SKILL,
    ENABLE_HIGH_SCORE,
    ENABLE_KEYBOARD_CONTROL,
    ENABLE_LEVEL_PROGRESS,
    ENABLE_LEVEL_SPEEDUP,
    ENABLE_MENU,
    ENABLE_OBSTACLES,
    ENABLE_PARTICLES,
    ENABLE_PAUSE,
    ENABLE_POWERUPS,
    ENABLE_RESET,
    ENABLE_SCORE,
    ENABLE_WEBCAM_PREVIEW,
    FPS,
    GRID_H,
    GRID_W,
    LEFT,
    POWER_DOUBLE,
    POWER_GHOST,
    POWER_SHIELD,
    POWER_SLOW,
    POWERUP_DURATION,
    POWERUP_SPAWN_SEC,
    RIGHT,
    SCORE_FILENAME,
    SCREEN_H,
    SCREEN_W,
    STATE_GAME_OVER,
    STATE_MENU,
    STATE_PAUSED,
    STATE_PLAYING,
    UP,
)
from entities import Food, PowerUp, Snake, make_particle_burst
from hand_tracker import HandTracker
from renderer import Renderer
from storage import load_scores, save_scores


class DisabledHandTracker:
    available = False

    def get_direction(self):
        return None

    def get_gesture(self):
        return None

    def get_status_label(self):
        return "KEYBOARD"

    def get_cam_frame(self):
        return None

    def stop(self):
        pass


class UpgradedGame:
    def __init__(self, model_path: str):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Snake Game - Finger Control Upgrade")
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.score_path = os.path.join(self.script_dir, SCORE_FILENAME)
        self.scores = load_scores(self.score_path) if ENABLE_HIGH_SCORE else {
            "best_score": 0,
            "last_score": 0,
            "games_played": 0,
            "best_level": 1,
        }
        self.difficulties = list(DIFFICULTIES.keys())
        self.difficulty_i = 1
        self.state = STATE_MENU if ENABLE_MENU else STATE_PLAYING
        self._reset_round()

        if ENABLE_GESTURE_CONTROL:
            print("\nMenginisialisasi MediaPipe HandLandmarker...")
            self.tracker = HandTracker(model_path)
        else:
            print("\nKontrol gesture dimatikan dari config. Gunakan keyboard.")
            self.tracker = DisabledHandTracker()

        if self.tracker.available:
            print("Game siap! Kontrol jari aktif.")
        else:
            print("Webcam tidak tersedia. Gunakan keyboard WASD.")

    @property
    def difficulty(self):
        return self.difficulties[self.difficulty_i]

    @property
    def hi_score(self):
        return self.scores["best_score"] if ENABLE_HIGH_SCORE else 0

    @property
    def show_cam(self):
        return ENABLE_WEBCAM_PREVIEW and self.tracker.available

    def _powerup_kinds(self):
        if ENABLE_ADVANCED_POWERUPS:
            return [POWER_SLOW, POWER_DOUBLE, POWER_SHIELD, POWER_GHOST]
        return [POWER_SLOW]

    def _reset_round(self):
        self.snake = Snake()
        self.food = Food()
        self.powerup = None
        self.obstacles = []
        self.particles = []
        self.effects = {}
        self.has_shield = False
        self.level = 1
        self.frame_n = 0
        self.last_power_spawn = time.monotonic()

    def _start_game(self):
        self._reset_round()
        self.state = STATE_PLAYING

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type != pygame.KEYDOWN:
                continue

            if self.state == STATE_MENU:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._start_game()
                elif ENABLE_DIFFICULTY_SELECT and event.key == pygame.K_TAB:
                    self.difficulty_i = (self.difficulty_i + 1) % len(self.difficulties)
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return False
            elif self.state == STATE_GAME_OVER:
                if ENABLE_RESET and event.key == pygame.K_r:
                    self._start_game()
                elif event.key == pygame.K_m:
                    self.state = STATE_MENU
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return False
            elif self.state == STATE_PAUSED:
                if ENABLE_PAUSE and event.key in (pygame.K_SPACE, pygame.K_p):
                    self.state = STATE_PLAYING
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return False
            else:
                if ENABLE_PAUSE and event.key in (pygame.K_SPACE, pygame.K_p):
                    self.state = STATE_PAUSED
                    continue
                if not ENABLE_KEYBOARD_CONTROL:
                    continue
                km = {
                    pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
                    pygame.K_LEFT: LEFT, pygame.K_a: LEFT,
                    pygame.K_UP: UP, pygame.K_w: UP,
                    pygame.K_DOWN: DOWN, pygame.K_s: DOWN,
                }
                if event.key in km:
                    self.snake.set_direction(km[event.key])
        return True

    def _handle_finger(self):
        gesture = self.tracker.get_gesture() if self.tracker.available else None
        if gesture == "PALM":
            if ENABLE_PAUSE and self.state == STATE_PLAYING:
                self.state = STATE_PAUSED
            elif ENABLE_PAUSE and self.state == STATE_PAUSED:
                self.state = STATE_PLAYING
        elif gesture == "FIST":
            if ENABLE_RESET and self.state in (STATE_MENU, STATE_GAME_OVER):
                self._start_game()
        elif (ENABLE_GESTURE_POWER_SKILL and gesture == "TWO_FINGERS" and
                self.state == STATE_PLAYING):
            self._activate_power(POWER_SLOW)

        d = self.tracker.get_direction()
        if d is not None and self.state == STATE_PLAYING:
            self.snake.set_direction(d)

    def _current_speed(self):
        base = DIFFICULTIES[self.difficulty]["speed"]
        speed = max(3, base - (self.level - 1)) if ENABLE_LEVEL_SPEEDUP else base
        if POWER_SLOW in self.effects:
            speed += 4
        return speed

    def _cleanup_effects(self):
        now = time.monotonic()
        for key in [k for k, until in self.effects.items() if until <= now]:
            del self.effects[key]

    def _activate_power(self, kind):
        if kind != POWER_SLOW and not ENABLE_ADVANCED_POWERUPS:
            return
        if kind == POWER_SHIELD:
            self.has_shield = True
        else:
            self.effects[kind] = time.monotonic() + POWERUP_DURATION

    def _spawn_particles(self, grid_pos, color, count=18):
        if not ENABLE_PARTICLES:
            return
        self.particles.extend(make_particle_burst(grid_pos, color, count))

    def _blocked_cells(self):
        blocked = set(self.snake.body)
        blocked.update(self.obstacles)
        blocked.add(self.food.pos)
        if self.powerup is not None:
            blocked.add(self.powerup.pos)
        return blocked

    def _update_level_and_obstacles(self):
        if not ENABLE_LEVEL_PROGRESS:
            return
        new_level = self.snake.score // 50 + 1
        if new_level == self.level:
            return
        self.level = new_level
        if (not ENABLE_OBSTACLES or not DIFFICULTIES[self.difficulty]["obstacles"] or
                self.level < 3):
            return
        target = min(18, (self.level - 2) * 3)
        while len(self.obstacles) < target:
            p = (random.randint(2, GRID_W-3), random.randint(3, GRID_H-3))
            if p not in self._blocked_cells():
                self.obstacles.append(p)
        self.food.respawn(self.snake.body, self.obstacles)

    def _finish_game(self):
        self.state = STATE_GAME_OVER
        if ENABLE_HIGH_SCORE:
            self.scores["last_score"] = self.snake.score
            self.scores["games_played"] += 1
            self.scores["best_score"] = max(self.scores["best_score"], self.snake.score)
            self.scores["best_level"] = max(self.scores["best_level"], self.level)
            save_scores(self.score_path, self.scores)
        self._spawn_particles(self.snake.head, (220, 50, 50), 40)

    def _update_particles(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

    def _update(self):
        self._update_particles()
        if self.state != STATE_PLAYING:
            return

        self.frame_n += 1
        self.food.update()
        if self.powerup is not None:
            self.powerup.update()
        self._cleanup_effects()
        self._update_level_and_obstacles()

        if (ENABLE_POWERUPS and self.powerup is None and
                time.monotonic() - self.last_power_spawn > POWERUP_SPAWN_SEC):
            self.powerup = PowerUp(self._blocked_cells(), self._powerup_kinds())
            self.last_power_spawn = time.monotonic()

        if self.frame_n % self._current_speed() != 0:
            return

        active_obstacles = self.obstacles if ENABLE_OBSTACLES else []
        ghost_active = ENABLE_ADVANCED_POWERUPS and POWER_GHOST in self.effects
        if not self.snake.move(active_obstacles, ignore_body=ghost_active,
                               ignore_obstacles=ghost_active):
            if ENABLE_ADVANCED_POWERUPS and self.has_shield:
                self.has_shield = False
                self.snake.alive = True
                self.effects[POWER_GHOST] = time.monotonic() + 2.0
                self._spawn_particles(self.snake.head, COLOR_SHIELD, 24)
                return
            self._finish_game()
            return

        if self.snake.head == self.food.pos:
            points = 20 if ENABLE_ADVANCED_POWERUPS and POWER_DOUBLE in self.effects else 10
            if not ENABLE_SCORE:
                points = 0
            self.snake.eat(points)
            self._spawn_particles(self.food.pos, COLOR_FOOD, 18)
            self.food.respawn(self.snake.body, self._blocked_cells())

        if ENABLE_POWERUPS and self.powerup is not None and self.snake.head == self.powerup.pos:
            kind = self.powerup.kind
            self._activate_power(kind)
            self._spawn_particles(self.powerup.pos, PowerUp.COLORS.get(kind, COLOR_POWERUP), 24)
            self.powerup = None

    def _render(self):
        if self.state == STATE_MENU:
            self.renderer.draw_menu(self.difficulty, self.scores, self.tracker.available)
            if self.show_cam:
                self.renderer.draw_cam(self.tracker.get_cam_frame())
            elif ENABLE_WEBCAM_PREVIEW:
                self.renderer.draw_no_cam()
            pygame.display.flip()
            return

        self.renderer.draw_grid(self.level)
        if ENABLE_OBSTACLES:
            self.renderer.draw_obstacles(self.obstacles)
        self.renderer.draw_food(self.food)
        if ENABLE_POWERUPS:
            self.renderer.draw_powerup(self.powerup)
        self.renderer.draw_snake(self.snake)
        self.renderer.draw_particles(self.particles)
        self.renderer.draw_score(self.snake.score, self.hi_score, self.level, self.difficulty)
        gesture_label = self.tracker.get_status_label() if self.tracker.available else "KEYBOARD"
        self.renderer.draw_effects(self.effects, self.has_shield, gesture_label)
        if self.show_cam:
            self.renderer.draw_cam(self.tracker.get_cam_frame())
        elif ENABLE_WEBCAM_PREVIEW:
            self.renderer.draw_no_cam()
        self.renderer.draw_hint(self.tracker.available)
        if self.state == STATE_PAUSED:
            self.renderer.draw_pause()
        elif self.state == STATE_GAME_OVER:
            self.renderer.draw_game_over(self.snake.score, self.hi_score, self.level, self.scores)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self._handle_events()
            self._handle_finger()
            self._update()
            self._render()
            self.clock.tick(FPS)

        print("\nMenutup game...")
        self.tracker.stop()
        pygame.quit()
        sys.exit()
