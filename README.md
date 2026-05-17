# Snake Finger Control

Game Snake berbasis Python yang bisa dimainkan dengan gerakan jari melalui webcam. Game ini memakai Pygame untuk tampilan, OpenCV untuk input kamera, dan MediaPipe HandLandmarker untuk membaca landmark tangan secara real-time.

Jika webcam tidak tersedia, game tetap bisa dimainkan dengan keyboard.

## Fitur

- Kontrol ular dengan gerakan jari telunjuk ke kanan, kiri, atas, atau bawah.
- Fallback keyboard menggunakan `WASD` atau tombol panah.
- Menu awal dengan pilihan difficulty: `Easy`, `Normal`, dan `Hard`.
- Pause dan resume melalui keyboard atau gesture telapak tangan.
- Gesture kepalan tangan untuk mulai atau restart dari menu/game over.
- High score permanen disimpan di `scores.json`.
- Efek partikel saat makan dan game over.
- Preview webcam di dalam layar game dengan visualisasi skeleton tangan.
- Feature flags di `config.py` untuk menyalakan atau mematikan fitur tambahan tanpa menghapus kode.

## Status Fitur Saat Ini

Fitur utama untuk demo saat ini aktif secara default:

| Fitur | Status Default |
| --- | --- |
| Kontrol gesture | Aktif |
| Kontrol keyboard | Aktif |
| Score | Aktif |
| High score | Aktif |
| Menu utama | Aktif |
| Pause/resume | Aktif |
| Restart/reset | Aktif |
| Pilihan difficulty | Aktif |
| Preview webcam | Aktif |
| Skeleton tangan | Aktif |
| Efek partikel dasar | Aktif |

Fitur tambahan berikut sudah tersedia di kode, tetapi default-nya dimatikan agar progress demo bisa bertahap:

| Fitur Tambahan | Status Default |
| --- | --- |
| Level progression | Nonaktif |
| Speed-up berdasarkan level | Nonaktif |
| Obstacle | Nonaktif |
| Random power-up | Nonaktif |
| Advanced power-up (`2X`, `SH`, `G`) | Nonaktif |
| Gesture dua jari untuk skill | Nonaktif |

## Requirement

- Python 3.10 atau lebih baru.
- Webcam, jika ingin memakai kontrol gesture.
- Dependency Python:
  - `pygame-ce`
  - `opencv-python-headless`
  - `mediapipe`
  - `numpy`

Catatan: gunakan `pygame-ce`, bukan package `pygame` biasa.

## Instalasi

1. Clone atau buka folder project ini.

```bash
cd snake-learn
```

2. Buat virtual environment.

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependency.

```bash
pip uninstall pygame -y
pip install pygame-ce opencv-python-headless mediapipe numpy
```

4. Jalankan game.

```bash
python snake_finger_control.py
```

Saat pertama kali dijalankan, aplikasi akan memastikan file model `hand_landmarker.task` tersedia. Jika file belum ada, aplikasi akan mencoba mengunduh model MediaPipe secara otomatis.

## Cara Bermain

Di menu awal:

| Input | Aksi |
| --- | --- |
| `Enter` / `Space` | Mulai game |
| `Tab` | Ganti difficulty |
| `Q` / `Esc` | Keluar |
| Kepalan tangan | Mulai game |

Saat bermain:

| Input | Aksi |
| --- | --- |
| Geser telunjuk ke kanan | Ular bergerak ke kanan |
| Geser telunjuk ke kiri | Ular bergerak ke kiri |
| Geser telunjuk ke atas | Ular bergerak ke atas |
| Geser telunjuk ke bawah | Ular bergerak ke bawah |
| Telapak tangan | Pause / resume |
| `WASD` / tombol panah | Kontrol keyboard |
| `Space` / `P` | Pause / resume |
| `Q` / `Esc` | Keluar |

Catatan: gesture dua jari untuk skill sudah ada di kode, tetapi default-nya dimatikan melalui `ENABLE_GESTURE_POWER_SKILL = False`.

Saat game over:

| Input | Aksi |
| --- | --- |
| `R` | Restart |
| `M` | Kembali ke menu |
| `Q` / `Esc` | Keluar |
| Kepalan tangan | Restart |

## Tips Kontrol Gesture

- Posisikan tangan di depan webcam dengan pencahayaan yang cukup.
- Gunakan jari telunjuk sebagai input arah utama.
- Gerakkan jari dengan jelas melewati threshold gerakan minimal.
- Jika gesture tidak stabil, coba jauhkan tangan sedikit dari kamera atau tingkatkan pencahayaan.
- Jika kamera gagal dibuka, game otomatis masuk mode keyboard.

## Struktur Project

```text
snake_finger_control.py  Entry point, cek dependency, cek model, lalu menjalankan game.
config.py                Konstanta dan feature flags untuk mengatur fitur aktif/nonaktif.
game.py                  Controller utama: menu, loop gameplay, skor, level, obstacle, power-up.
hand_tracker.py          Thread webcam, MediaPipe HandLandmarker, arah jari, dan event gesture.
gestures.py              Klasifikasi gesture sederhana: telapak, kepalan, dan dua jari.
entities.py              Entity game: Snake, Food, PowerUp, Particle.
renderer.py              Rendering UI, arena, snake, power-up, webcam preview, dan overlay.
model_utils.py           Validasi dan download model MediaPipe.
storage.py               Load/save high score ke scores.json.
scores.json              Data skor lokal.
hand_landmarker.task     Model MediaPipe HandLandmarker.
FITUR.md                 Ringkasan fitur dan modularisasi project.
```

## Konfigurasi

Pengaturan utama ada di `config.py`.

```python
SCREEN_W, SCREEN_H = 800, 600
CELL_SIZE = 20
FPS = 60
SNAKE_SPEED = 8
FINGER_THRESHOLD = 25
CAM_W, CAM_H = 200, 150
POWERUP_DURATION = 8.0
POWERUP_SPAWN_SEC = 7.0
```

Feature flags utama juga ada di `config.py`.

```python
# Fitur utama presentasi.
ENABLE_GESTURE_CONTROL = True
ENABLE_KEYBOARD_CONTROL = True
ENABLE_SCORE = True
ENABLE_HIGH_SCORE = True
ENABLE_MENU = True
ENABLE_PAUSE = True
ENABLE_RESET = True
ENABLE_DIFFICULTY_SELECT = True
ENABLE_WEBCAM_PREVIEW = True
ENABLE_HAND_SKELETON = True

# Fitur tambahan untuk milestone berikutnya.
ENABLE_LEVEL_PROGRESS = False
ENABLE_LEVEL_SPEEDUP = False
ENABLE_OBSTACLES = False
ENABLE_POWERUPS = False
ENABLE_ADVANCED_POWERUPS = False
ENABLE_PARTICLES = True
ENABLE_GESTURE_POWER_SKILL = False
```

Difficulty juga diatur di `config.py`.

```python
DIFFICULTIES = {
    "Easy": {"speed": 10, "obstacles": False},
    "Normal": {"speed": 8, "obstacles": True},
    "Hard": {"speed": 6, "obstacles": True},
}
```

Nilai `speed` yang lebih kecil berarti ular bergerak lebih cepat.

Catatan: obstacle pada difficulty `Normal` dan `Hard` baru dipakai jika `ENABLE_OBSTACLES = True` dan level progression aktif.

## Troubleshooting

### Webcam tidak ditemukan

- Pastikan webcam tersambung dan tidak sedang dipakai aplikasi lain.
- Cek izin kamera di sistem operasi.
- Jalankan ulang game.
- Gunakan `WASD` atau tombol panah sebagai fallback.

### ModuleNotFoundError untuk pygame, cv2, mediapipe, atau numpy

Install ulang dependency:

```bash
pip uninstall pygame -y
pip install pygame-ce opencv-python-headless mediapipe numpy
```

### Model MediaPipe gagal diunduh

Download manual file model dari:

```text
https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

Simpan dengan nama `hand_landmarker.task` di folder yang sama dengan `snake_finger_control.py`.

### Gesture terasa lambat atau tidak responsif

- Pastikan pencahayaan cukup.
- Gerakkan jari lebih jelas.
- Ubah `FINGER_THRESHOLD` di `config.py` ke nilai lebih kecil, misalnya `15` atau `20`.
- Tutup aplikasi lain yang memakai kamera.

## Menyimpan Skor

Skor terbaik, skor terakhir, total permainan, dan level terbaik disimpan di `scores.json`. File ini akan diperbarui otomatis setelah game over.

Penyimpanan high score aktif jika `ENABLE_HIGH_SCORE = True`.

## Fitur Tambahan yang Bisa Diaktifkan Nanti

Beberapa fitur sengaja dimatikan dulu untuk kebutuhan progress presentasi. Untuk mengaktifkannya, ubah nilai feature flag di `config.py` dari `False` menjadi `True`.

- `ENABLE_LEVEL_PROGRESS`: mengaktifkan kenaikan level berdasarkan skor.
- `ENABLE_LEVEL_SPEEDUP`: membuat ular semakin cepat saat level naik.
- `ENABLE_OBSTACLES`: menampilkan obstacle pada level tertentu.
- `ENABLE_POWERUPS`: mengaktifkan spawn power-up acak.
- `ENABLE_ADVANCED_POWERUPS`: mengaktifkan power-up lanjutan seperti double score, shield, dan ghost.
- `ENABLE_GESTURE_POWER_SKILL`: mengaktifkan gesture dua jari untuk skill slow motion.

## Lisensi

Project ini bebas digunakan dan dimodifikasi untuk belajar atau eksperimen.
