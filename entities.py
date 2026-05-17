import random

import numpy as np

from config import (
    CELL_SIZE,
    DOWN,
    GRID_H,
    GRID_W,
    LEFT,
    POWER_DOUBLE,
    POWER_GHOST,
    POWER_SHIELD,
    POWER_SLOW,
    RIGHT,
    UP,
)


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        sx, sy = GRID_W // 2, GRID_H // 2
        self.body = [(sx, sy), (sx-1, sy), (sx-2, sy)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.score = 0
        self.alive = True
        self.grow_pending = 0

    @property
    def head(self):
        return self.body[0]

    def next_head(self):
        hx, hy = self.head
        dx, dy = self.next_direction
        return (hx + dx) % GRID_W, (hy + dy) % GRID_H

    def set_direction(self, new_dir):
        opposite = {RIGHT: LEFT, LEFT: RIGHT, UP: DOWN, DOWN: UP}
        if new_dir != opposite.get(self.direction):
            self.next_direction = new_dir

    def move(self, obstacles=None, ignore_body=False, ignore_obstacles=False):
        if not self.alive:
            return False
        obstacles = set(obstacles or [])
        self.direction = self.next_direction
        nx, ny = self.next_head()

        if ((not ignore_body and (nx, ny) in self.body) or
                (not ignore_obstacles and (nx, ny) in obstacles)):
            self.alive = False
            return False

        self.body.insert(0, (nx, ny))
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
        return True

    def eat(self, points=10):
        self.grow_pending += 1
        self.score += points


class Food:
    def __init__(self):
        self.pos = self._rand()
        self._pulse = 0.0

    def _rand(self):
        return (random.randint(0, GRID_W-1), random.randint(0, GRID_H-1))

    def respawn(self, snake_body, blocked=None):
        blocked = set(blocked or [])
        while True:
            p = self._rand()
            if p not in snake_body and p not in blocked:
                self.pos = p
                break

    def update(self):
        self._pulse = (self._pulse + 0.1) % (2 * np.pi)

    @property
    def pulse(self):
        return (np.sin(self._pulse) + 1) / 2


class PowerUp:
    COLORS = {
        POWER_SLOW: (80, 180, 255),
        POWER_DOUBLE: (255, 210, 80),
        POWER_SHIELD: (90, 210, 255),
        POWER_GHOST: (190, 130, 255),
    }
    LABELS = {
        POWER_SLOW: "S",
        POWER_DOUBLE: "2X",
        POWER_SHIELD: "SH",
        POWER_GHOST: "G",
    }

    def __init__(self, blocked, kinds=None):
        self.kind = random.choice(kinds or [POWER_SLOW, POWER_DOUBLE, POWER_SHIELD, POWER_GHOST])
        self.pos = self._rand(blocked)
        self._pulse = 0.0

    def _rand(self, blocked):
        blocked = set(blocked or [])
        while True:
            p = (random.randint(0, GRID_W-1), random.randint(0, GRID_H-1))
            if p not in blocked:
                return p

    def update(self):
        self._pulse = (self._pulse + 0.12) % (2 * np.pi)

    @property
    def pulse(self):
        return (np.sin(self._pulse) + 1) / 2


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2.4, 2.4)
        self.vy = random.uniform(-2.4, 2.4)
        self.color = color
        self.life = random.randint(22, 38)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.94
        self.vy *= 0.94
        self.life -= 1

    @property
    def alive(self):
        return self.life > 0


def make_particle_burst(grid_pos, color, count=18):
    px = grid_pos[0] * CELL_SIZE + CELL_SIZE // 2
    py = grid_pos[1] * CELL_SIZE + CELL_SIZE // 2
    return [Particle(px, py, color) for _ in range(count)]
