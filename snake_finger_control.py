import pygame
import cv2
import mediapipe as mp
import numpy as np
import random
import sys
import threading
import time
import urllib.request
import os

# ─────────────────────────────────────────────────
#  KONSTANTA & KONFIGURASI
# ─────────────────────────────────────────────────

SCREEN_W, SCREEN_H  = 800, 600
CELL_SIZE           = 20
GRID_W              = SCREEN_W // CELL_SIZE   # 40 kolom
GRID_H              = SCREEN_H // CELL_SIZE   # 30 baris
FPS                 = 60
SNAKE_SPEED         = 8    # ular bergerak setiap N frame (lebih kecil = lebih cepat)
FINGER_THRESHOLD    = 25   # min pixel delta agar arah berubah
CAM_W, CAM_H        = 200, 150

# Model MediaPipe Tasks (didownload otomatis jika belum ada)
MODEL_FILENAME = "hand_landmarker.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)

# Arah gerak (dx, dy)
RIGHT = ( 1,  0)
LEFT  = (-1,  0)
UP    = ( 0, -1)
DOWN  = ( 0,  1)

# Warna
COLOR_BG          = (10,  10,  20)
COLOR_GRID        = (20,  20,  35)
COLOR_SNAKE_HEAD  = (0,  230, 120)
COLOR_SNAKE_BODY  = (0,  170,  90)
COLOR_SNAKE_SHINE = (100, 255, 180)
COLOR_FOOD        = (255,  70,  70)
COLOR_FOOD_SHINE  = (255, 180, 150)
COLOR_TEXT        = (220, 220, 220)
COLOR_SCORE       = (0,  230, 120)
COLOR_CAM_BORDER  = (0,  200, 100)
COLOR_WARNING     = (255, 180,   0)

# Index landmark ujung jari telunjuk di MediaPipe (nomor 8)
INDEX_FINGER_TIP  = 8

# Koneksi antar landmark tangan untuk menggambar skeleton
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),        # Jempol
    (0,5),(5,6),(6,7),(7,8),        # Telunjuk
    (0,9),(9,10),(10,11),(11,12),   # Tengah
    (0,13),(13,14),(14,15),(15,16), # Manis
    (0,17),(17,18),(18,19),(19,20), # Kelingking
    (5,9),(9,13),(13,17),           # Telapak atas
]


# ─────────────────────────────────────────────────
#  HELPER: Download model jika belum ada
# ─────────────────────────────────────────────────

def ensure_model(model_path: str) -> bool:
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"✅ Model ditemukan: {model_path} ({size_mb:.1f} MB)")
        return True

    print(f"\n📥 Model MediaPipe belum ada, mendownload...")
    print(f"   File : {MODEL_FILENAME}")
    print(f"   URL  : {MODEL_URL}")
    print("   Size : ~5 MB — harap tunggu...\n")

    try:
        def _progress(count, block_size, total_size):
            if total_size > 0:
                pct = int(count * block_size * 100 / total_size)
                print(f"\r   Progress: {min(pct, 100)}%", end="", flush=True)

        urllib.request.urlretrieve(MODEL_URL, model_path, reporthook=_progress)
        print(f"\n✅ Berhasil didownload: {model_path}")
        return True
    except Exception as e:
        print(f"\n❌ Gagal download model: {e}")
        print("\n   Solusi: Download manual dari link berikut:")
        print(f"   {MODEL_URL}")
        print(f"   Simpan sebagai '{MODEL_FILENAME}' di folder yang sama dengan script ini.")
        return False


# ─────────────────────────────────────────────────
#  CLASS: HandTracker  (Thread OpenCV + MediaPipe Tasks API)
# ─────────────────────────────────────────────────

class HandTracker:
    def __init__(self, model_path: str):
        # ── Import MediaPipe Tasks API (versi baru) ──
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision as mp_vision

        self._mp        = mp
        self._mp_vision = mp_vision
        self._mp_python = mp_python

        # ── Buka webcam ──
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("⚠  Webcam tidak ditemukan! Gunakan keyboard WASD sebagai fallback.")
            self.available = False
        else:
            self.available = True

        # ── Inisialisasi HandLandmarker ──
        if self.available:
            try:
                # Konfigurasi opsi HandLandmarker
                base_opts = mp_python.BaseOptions(model_asset_path=model_path)
                options   = mp_vision.HandLandmarkerOptions(
                    base_options=base_opts,
                    # VIDEO mode: harus kirim timestamp yang terus naik
                    running_mode=mp_vision.RunningMode.VIDEO,
                    num_hands=1,
                    min_hand_detection_confidence=0.5,
                    min_hand_presence_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
                self._detector = mp_vision.HandLandmarker.create_from_options(options)
                print("✅ MediaPipe HandLandmarker (Tasks API) berhasil diinisialisasi.")
            except Exception as e:
                print(f"❌ Gagal membuat HandLandmarker: {e}")
                self.available = False

        # ── Shared state antar thread (dilindungi Lock) ──
        self._lock            = threading.Lock()
        self._direction       = None   # Arah gerakan jari terbaru
        self._cam_frame       = None   # Frame BGR untuk preview di game
        self._prev_finger_pos = None   # Posisi jari frame sebelumnya (px, py)
        self._running         = True

        # ── Mulai thread background ──
        if self.available:
            self._thread = threading.Thread(
                target=self._tracking_loop, daemon=True
            )
            self._thread.start()

    def _draw_hand_skeleton(self, frame, landmarks_px):
        # Garis penghubung antar landmark
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, landmarks_px[a], landmarks_px[b], (0, 160, 80), 2)

        # Titik setiap landmark
        for i, (lx, ly) in enumerate(landmarks_px):
            if i == INDEX_FINGER_TIP:
                # Jari telunjuk: kuning dan lebih besar
                cv2.circle(frame, (lx, ly), 12, (0, 200, 60), -1)
                cv2.circle(frame, (lx, ly),  8, (255, 220, 0), -1)
            else:
                cv2.circle(frame, (lx, ly), 4, (0, 220, 120), -1)

    def _tracking_loop(self):
        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            # Mirror frame agar gerakan terasa intuitif (efek cermin)
            frame = cv2.flip(frame, 1)
            h, w  = frame.shape[:2]

            # ── Buat MediaPipe Image object dari frame BGR ──
            # Tasks API memerlukan object mp.Image, bukan numpy array langsung
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = self._mp.Image(
                image_format=self._mp.ImageFormat.SRGB,
                data=rgb
            )

            # ── Timestamp monotonic dalam milidetik ──
            timestamp_ms = int(time.monotonic() * 1000)

            # ── Jalankan deteksi ──
            try:
                result = self._detector.detect_for_video(mp_image, timestamp_ms)
            except Exception:
                time.sleep(0.01)
                continue

            detected_direction = None

            if result.hand_landmarks:
                # Ambil data tangan pertama yang terdeteksi
                hand = result.hand_landmarks[0]

                # ── Konversi landmark normalisasi (0.0–1.0) → koordinat pixel ──
                landmarks_px = [
                    (int(lm.x * w), int(lm.y * h))
                    for lm in hand
                ]

                # ── Gambar skeleton tangan ──
                self._draw_hand_skeleton(frame, landmarks_px)

                # ── Ambil posisi ujung jari telunjuk ──
                curr_x, curr_y = landmarks_px[INDEX_FINGER_TIP]

                # Label koordinat
                cv2.putText(frame, f"({curr_x},{curr_y})",
                            (curr_x + 14, curr_y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 255, 200), 1)

                # ── Hitung pergeseran (delta) dari posisi sebelumnya ──
                if self._prev_finger_pos is not None:
                    prev_x, prev_y = self._prev_finger_pos
                    dx = curr_x - prev_x   # + = geser kanan
                    dy = curr_y - prev_y   # + = geser bawah (Y koordinat webcam)

                    # Hanya ubah arah jika gerakan melebihi threshold
                    # dan ambil komponen yang lebih dominan (X atau Y)
                    if max(abs(dx), abs(dy)) > FINGER_THRESHOLD:
                        if abs(dx) >= abs(dy):
                            # Gerakan horizontal dominan
                            detected_direction = RIGHT if dx > 0 else LEFT
                        else:
                            # Gerakan vertikal dominan
                            # dy positif = jari bergerak ke bawah di webcam
                            # = ular bergerak ke BAWAH (koordinat game sama arahnya)
                            detected_direction = DOWN if dy > 0 else UP

                # Update posisi sebelumnya
                self._prev_finger_pos = (curr_x, curr_y)

            else:
                # Tidak ada tangan terdeteksi — reset agar tidak ada drift
                self._prev_finger_pos = None
                cv2.putText(frame, "Arahkan jari ke kamera",
                            (8, 28), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (80, 80, 220), 1)

            # Info threshold
            cv2.putText(frame, f"Min geser: {FINGER_THRESHOLD}px",
                        (5, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                        (120, 120, 120), 1)

            # ── Simpan ke shared variable (thread-safe) ──
            with self._lock:
                self._direction = detected_direction
                # Resize ke ukuran display mini
                self._cam_frame = cv2.resize(frame, (CAM_W, CAM_H))

    def get_direction(self):
        with self._lock:
            d = self._direction
            self._direction = None
        return d

    def get_cam_frame(self):
        with self._lock:
            return self._cam_frame.copy() if self._cam_frame is not None else None

    def stop(self):
        self._running = False
        if self.available:
            self.cap.release()
            try:
                self._detector.close()
            except Exception:
                pass


# ─────────────────────────────────────────────────
#  CLASS: Snake
# ─────────────────────────────────────────────────

class Snake:

    def __init__(self):
        self.reset()

    def reset(self):
        sx, sy = GRID_W // 2, GRID_H // 2
        # Ular awal 3 segmen, bergerak ke kanan
        self.body           = [(sx, sy), (sx-1, sy), (sx-2, sy)]
        self.direction      = RIGHT
        self.next_direction = RIGHT
        self.score          = 0
        self.alive          = True
        self.grow_pending   = 0

    @property
    def head(self):
        return self.body[0]

    def set_direction(self, new_dir):
        opposite = {RIGHT: LEFT, LEFT: RIGHT, UP: DOWN, DOWN: UP}
        if new_dir != opposite.get(self.direction):
            self.next_direction = new_dir

    def move(self):
        if not self.alive:
            return False

        self.direction = self.next_direction
        hx, hy = self.head
        dx, dy = self.direction

        # Wrap-around: jika keluar tepi, muncul di sisi berlawanan
        nx, ny = (hx + dx) % GRID_W, (hy + dy) % GRID_H

        # Cek tabrakan dengan tubuh sendiri
        if (nx, ny) in self.body:
            self.alive = False
            return False

        self.body.insert(0, (nx, ny))

        # Pertumbuhan: jika grow_pending > 0, jangan hapus ekor
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

        return True

    def eat(self):
        self.grow_pending += 1
        self.score += 10


# ─────────────────────────────────────────────────
#  CLASS: Food
# ─────────────────────────────────────────────────

class Food:
    def __init__(self):
        self.pos    = self._rand()
        self._pulse = 0.0   # Untuk efek animasi denyutan

    def _rand(self):
        return (random.randint(0, GRID_W-1), random.randint(0, GRID_H-1))

    def respawn(self, snake_body):
        while True:
            p = self._rand()
            if p not in snake_body:
                self.pos = p
                break

    def update(self):
        self._pulse = (self._pulse + 0.1) % (2 * np.pi)

    @property
    def pulse(self):
        return (np.sin(self._pulse) + 1) / 2


# ─────────────────────────────────────────────────
#  CLASS: Renderer
# ─────────────────────────────────────────────────

class Renderer:

    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.f_large  = pygame.font.SysFont("Consolas", 48, bold=True)
        self.f_medium = pygame.font.SysFont("Consolas", 28, bold=True)
        self.f_small  = pygame.font.SysFont("Consolas", 18)
        self.f_tiny   = pygame.font.SysFont("Consolas", 14)

    def draw_grid(self):
        self.screen.fill(COLOR_BG)
        for x in range(0, SCREEN_W, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (SCREEN_W, y))

    def draw_snake(self, snake):
        for i, (cx, cy) in enumerate(snake.body):
            r = pygame.Rect(cx*CELL_SIZE+1, cy*CELL_SIZE+1, CELL_SIZE-2, CELL_SIZE-2)
            if i == 0:
                # Kepala: lebih terang + efek highlight
                pygame.draw.rect(self.screen, COLOR_SNAKE_HEAD, r, border_radius=4)
                pygame.draw.rect(self.screen, COLOR_SNAKE_SHINE,
                                 pygame.Rect(r.x+2, r.y+2, 5, 5), border_radius=2)
                self._draw_eyes(cx, cy, snake.direction)
            else:
                # Tubuh: makin ke belakang makin gelap
                fade = max(0.4, 1.0 - i * 0.015)
                c = tuple(int(v * fade) for v in COLOR_SNAKE_BODY)
                pygame.draw.rect(self.screen, c, r, border_radius=3)

    def _draw_eyes(self, cx, cy, direction):
        bx, by = cx * CELL_SIZE, cy * CELL_SIZE
        half   = CELL_SIZE // 2
        offsets = {
            RIGHT: [(CELL_SIZE-5, half-3), (CELL_SIZE-5, half+3)],
            LEFT:  [(5, half-3),           (5, half+3)],
            UP:    [(half-3, 5),           (half+3, 5)],
            DOWN:  [(half-3, CELL_SIZE-5), (half+3, CELL_SIZE-5)],
        }
        for ox, oy in offsets.get(direction, []):
            pygame.draw.circle(self.screen, (20, 20, 20), (bx+ox, by+oy), 2)

    def draw_food(self, food):
        fx, fy = food.pos
        size   = int(CELL_SIZE * 0.8 + food.pulse * CELL_SIZE * 0.2)
        off    = (CELL_SIZE - size) // 2
        r = pygame.Rect(fx*CELL_SIZE+off, fy*CELL_SIZE+off, size, size)
        pygame.draw.rect(self.screen, COLOR_FOOD, r, border_radius=size//3)
        pygame.draw.rect(self.screen, COLOR_FOOD_SHINE,
                         pygame.Rect(r.x+2, r.y+2, 4, 4), border_radius=2)

    def draw_score(self, score, hi):
        self.screen.blit(
            self.f_medium.render(f"SCORE: {score:04d}", True, COLOR_SCORE), (10, 10))
        self.screen.blit(
            self.f_small.render(f"BEST:  {hi:04d}", True, (150, 200, 150)), (10, 44))

    def draw_cam(self, frame_bgr):
        if frame_bgr is None:
            return
        rgb  = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        surf = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
        cx   = SCREEN_W - CAM_W - 10
        cy   = 10
        # Border hijau
        pygame.draw.rect(self.screen, COLOR_CAM_BORDER,
                         pygame.Rect(cx-2, cy-2, CAM_W+4, CAM_H+4), border_radius=4)
        self.screen.blit(surf, (cx, cy))
        self.screen.blit(
            self.f_tiny.render("WEBCAM", True, COLOR_CAM_BORDER),
            (cx, cy + CAM_H + 4))

    def draw_no_cam(self):
        """Tampilkan placeholder jika webcam tidak tersedia."""
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
        hint = ("Gerakkan jari telunjuk untuk mengarahkan ular"
                if has_cam else "WASD / Arrow Keys untuk kontrol keyboard")
        self.screen.blit(self.f_tiny.render(hint, True, (80, 80, 100)),
                         (10, SCREEN_H - 20))

    def draw_game_over(self, score, hi):
        # Latar semi-transparan
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        self.screen.blit(ov, (0, 0))
        # Kotak tengah
        bw, bh = 520, 260
        bx     = (SCREEN_W - bw) // 2
        by     = (SCREEN_H - bh) // 2
        br     = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(self.screen, (20, 10, 10), br, border_radius=12)
        pygame.draw.rect(self.screen, (180, 30, 30), br, 2, border_radius=12)
        # Teks
        cx = SCREEN_W // 2
        def bc(surf, y):
            self.screen.blit(surf, (cx - surf.get_width()//2, y))
        bc(self.f_large.render("GAME OVER", True, (220, 50, 50)),  by+20)
        bc(self.f_medium.render(f"Skor: {score}", True, COLOR_TEXT), by+90)
        bc(self.f_small.render(f"Skor Tertinggi: {hi}", True, COLOR_SCORE), by+125)
        bc(self.f_small.render("Tekan 'R' untuk Restart", True, (180,180,180)), by+175)
        bc(self.f_small.render("Tekan 'Q' untuk Keluar",  True, (120,120,120)), by+205)


# ─────────────────────────────────────────────────
#  CLASS: Game  (Controller utama)
# ─────────────────────────────────────────────────

class Game:

    def __init__(self, model_path: str):
        pygame.init()
        self.screen    = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("🐍 Snake Game – Finger Control")
        self.clock     = pygame.time.Clock()
        self.renderer  = Renderer(self.screen)
        self.snake     = Snake()
        self.food      = Food()
        self.hi_score  = 0
        self.frame_n   = 0
        self.game_over = False

        print("\n🔍 Menginisialisasi MediaPipe HandLandmarker...")
        self.tracker = HandTracker(model_path)
        if self.tracker.available:
            print("🎮 Game siap! Kontrol jari aktif.")
        else:
            print("⌨  Webcam tidak tersedia. Gunakan keyboard WASD.")

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self._restart()
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        return False
                else:
                    # Keyboard fallback
                    km = {
                        pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
                        pygame.K_LEFT:  LEFT,  pygame.K_a: LEFT,
                        pygame.K_UP:    UP,    pygame.K_w: UP,
                        pygame.K_DOWN:  DOWN,  pygame.K_s: DOWN,
                    }
                    if event.key in km:
                        self.snake.set_direction(km[event.key])
        return True

    def _handle_finger(self):
        d = self.tracker.get_direction()
        if d is not None and not self.game_over:
            self.snake.set_direction(d)

    def _update(self):
        if self.game_over:
            return
        self.frame_n += 1
        self.food.update()

        # Ular bergerak setiap SNAKE_SPEED frame
        if self.frame_n % SNAKE_SPEED == 0:
            if not self.snake.move():
                self.game_over = True
                self.hi_score  = max(self.hi_score, self.snake.score)
                return
            # Cek apakah kepala memakan makanan
            if self.snake.head == self.food.pos:
                self.snake.eat()
                self.food.respawn(self.snake.body)

    def _render(self):
        self.renderer.draw_grid()
        self.renderer.draw_food(self.food)
        self.renderer.draw_snake(self.snake)
        self.renderer.draw_score(self.snake.score, self.hi_score)
        if self.tracker.available:
            self.renderer.draw_cam(self.tracker.get_cam_frame())
        else:
            self.renderer.draw_no_cam()
        self.renderer.draw_hint(self.tracker.available)
        if self.game_over:
            self.renderer.draw_game_over(self.snake.score, self.hi_score)
        pygame.display.flip()

    def _restart(self):
        self.snake     = Snake()
        self.food      = Food()
        self.frame_n   = 0
        self.game_over = False

    def run(self):
        running = True
        while running:
            running = self._handle_events()
            self._handle_finger()
            self._update()
            self._render()
            self.clock.tick(FPS)

        # Cleanup
        print("\n👋 Menutup game...")
        self.tracker.stop()
        pygame.quit()
        sys.exit()


# ─────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  🐍 SNAKE GAME – FINGER GESTURE CONTROL")
    print("  pygame-ce + opencv-python-headless + mediapipe")
    print("=" * 60)

    # ── Cek semua dependencies ──
    print("\n🔧 Mengecek dependencies...")
    errors = []
    for pkg, install_cmd in [
        ("pygame",    "pip uninstall pygame -y && pip install pygame-ce"),
        ("cv2",       "pip install opencv-python-headless"),
        ("mediapipe", "pip install mediapipe"),
        ("numpy",     "pip install numpy"),
    ]:
        try:
            __import__(pkg)
            print(f"   ✅ {pkg}")
        except ImportError:
            print(f"   ❌ {pkg}  →  {install_cmd}")
            errors.append(pkg)

    if errors:
        print(f"\nJalankan perintah install di atas lalu coba lagi.")
        sys.exit(1)

    # Tampilkan versi MediaPipe
    import mediapipe as _mp
    print(f"\n   MediaPipe versi: {getattr(_mp, '__version__', '?')}")

    # ── Pastikan model HandLandmarker tersedia ──
    # Model disimpan di folder yang sama dengan script ini
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, MODEL_FILENAME)

    if not ensure_model(model_path):
        print("\nGame tidak dapat dijalankan tanpa model MediaPipe.")
        sys.exit(1)

    # ── Mulai game ──
    print("\n🎮 Memulai game...")
    game = Game(model_path)
    game.run()