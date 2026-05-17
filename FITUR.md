# Daftar Fitur Snake Finger Control

Dokumen ini merangkum fitur yang sudah dibuat di project `snake-learn`, termasuk pembagian modul yang ada di dalam kode.

## Ringkasan

`snake-learn` adalah game Snake berbasis Python yang bisa dimainkan dengan gesture jari melalui webcam. Project ini memakai:

- `pygame-ce` untuk tampilan dan loop game.
- `opencv-python-headless` untuk akses kamera.
- `mediapipe` untuk deteksi landmark tangan.
- `numpy` untuk perhitungan efek visual sederhana.

Jika webcam tidak tersedia, game tetap bisa dimainkan menggunakan keyboard.

## Fitur Gameplay

- Game Snake klasik dengan arena grid.
- Ular bergerak secara otomatis sesuai arah terakhir.
- Makanan muncul ulang setelah dimakan.
- Ular bertambah panjang setelah makan.
- Skor bertambah saat makanan dimakan.
- State game lengkap:
  - Menu utama.
  - Playing.
  - Paused.
  - Game over.
- Restart game dari layar game over.
- Kembali ke menu dari layar game over.
- Keluar dari game melalui keyboard.
- Wrap-around arena: ular yang melewati tepi layar akan muncul dari sisi seberangnya.

## Fitur Kontrol

### Gesture Tangan

- Kontrol arah ular memakai gerakan jari telunjuk:
  - Geser ke kanan.
  - Geser ke kiri.
  - Geser ke atas.
  - Geser ke bawah.
- Gesture telapak tangan (`PALM`) untuk pause dan resume.
- Gesture kepalan tangan (`FIST`) untuk mulai game atau restart.
- Gesture dua jari (`TWO_FINGERS`) untuk mengaktifkan efek slow motion.
- Threshold gerakan jari dapat diatur melalui `FINGER_THRESHOLD` di `config.py`.

### Keyboard

- Fallback keyboard otomatis jika webcam tidak tersedia.
- Kontrol arah dengan:
  - `W`, `A`, `S`, `D`.
  - Tombol panah.
- `Enter` atau `Space` untuk mulai game dari menu.
- `Tab` untuk mengganti difficulty.
- `Space` atau `P` untuk pause/resume.
- `R` untuk restart saat game over.
- `M` untuk kembali ke menu saat game over.
- `Q` atau `Esc` untuk keluar.

## Fitur Difficulty

Game memiliki 3 tingkat difficulty:

| Difficulty | Speed Dasar | Obstacle |
| --- | ---: | --- |
| Easy | 10 | Tidak |
| Normal | 8 | Ya |
| Hard | 6 | Ya |

Catatan: nilai speed yang lebih kecil berarti ular bergerak lebih cepat.

## Fitur Level Progression

- Level dihitung dari skor.
- Setiap kelipatan 50 skor menaikkan level.
- Semakin tinggi level, semakin cepat ular bergerak.
- Pada difficulty `Normal` dan `Hard`, obstacle mulai muncul di level 3.
- Jumlah obstacle bertambah seiring kenaikan level.
- Jumlah obstacle dibatasi maksimal 18.

## Fitur Obstacle

- Obstacle muncul pada level tinggi untuk difficulty `Normal` dan `Hard`.
- Obstacle tidak ditempatkan di posisi ular, makanan, atau power-up.
- Menabrak obstacle menyebabkan game over.
- Obstacle bisa dilewati sementara saat efek ghost aktif.

## Fitur Power-Up

Power-up muncul otomatis secara berkala.

| Power-Up | Label | Efek |
| --- | --- | --- |
| Slow | `S` | Memperlambat gerakan ular sementara. |
| Double Score | `2X` | Menggandakan poin makanan sementara. |
| Shield | `SH` | Melindungi dari satu tabrakan. |
| Ghost | `G` | Membuat ular bisa melewati badan sendiri dan obstacle sementara. |

Detail tambahan:

- Durasi efek power-up diatur oleh `POWERUP_DURATION`.
- Interval spawn power-up diatur oleh `POWERUP_SPAWN_SEC`.
- Shield tidak memakai timer, tetapi habis setelah menyerap satu tabrakan.
- Jika shield aktif dan ular menabrak, shield hilang dan ghost aktif singkat sebagai perlindungan lanjutan.

## Fitur Skor dan Penyimpanan

- Skor bertambah 10 saat makan makanan biasa.
- Skor bertambah 20 jika efek double score aktif.
- Data skor disimpan permanen ke `scores.json`.
- Data yang disimpan:
  - `best_score`
  - `last_score`
  - `games_played`
  - `best_level`
- Jika file skor belum ada, game memakai nilai default.
- Jika file skor rusak atau gagal dibaca, game tetap berjalan dengan nilai default.

## Fitur Visual dan UI

- Tampilan arena berbasis grid.
- Warna latar berubah tipis sesuai level.
- Kepala dan badan ular memiliki warna berbeda.
- Kepala ular memiliki mata yang mengikuti arah gerak.
- Makanan memiliki efek pulse.
- Power-up memiliki warna dan label berbeda.
- Obstacle digambar sebagai blok berbeda.
- Efek partikel muncul saat:
  - Ular makan makanan.
  - Ular mengambil power-up.
  - Shield menyerap tabrakan.
  - Game over.
- UI menampilkan:
  - Score.
  - Best score.
  - Level.
  - Difficulty.
  - Efek aktif.
  - Status gesture.
- Overlay pause.
- Overlay game over.
- Menu utama dengan pilihan difficulty dan status webcam.

## Fitur Webcam Preview

- Preview webcam ditampilkan di dalam layar game.
- Skeleton tangan digambar di atas preview kamera.
- Ujung jari telunjuk diberi penanda khusus.
- Koordinat ujung jari ditampilkan di preview.
- Label gesture aktif ditampilkan di preview.
- Jika kamera tidak tersedia, game menampilkan panel informasi mode keyboard.

## Fitur MediaPipe Model

- Saat startup, game mengecek file `hand_landmarker.task`.
- Jika model sudah ada, game langsung menggunakannya.
- Jika model belum ada, game mencoba mengunduh otomatis dari URL MediaPipe.
- Jika download gagal, game menampilkan instruksi download manual.
- Game tidak dilanjutkan jika model MediaPipe tidak tersedia.

## Modularisasi Project

Project sudah dipisah menjadi beberapa modul dengan tanggung jawab yang cukup jelas.

| File | Tanggung Jawab |
| --- | --- |
| `snake_finger_control.py` | Entry point aplikasi, cek dependency, validasi model, lalu menjalankan game. |
| `config.py` | Konfigurasi global seperti ukuran layar, warna, arah, state, difficulty, power-up, kamera, dan model. |
| `game.py` | Controller utama game: state, loop, event keyboard, gesture, skor, level, obstacle, power-up, dan render orchestration. |
| `entities.py` | Entity game seperti `Snake`, `Food`, `PowerUp`, `Particle`, dan helper partikel. |
| `hand_tracker.py` | Akses webcam, thread tracking, MediaPipe HandLandmarker, deteksi arah jari, dan event gesture. |
| `gestures.py` | Klasifikasi gesture sederhana berbasis landmark tangan. |
| `renderer.py` | Semua logic rendering: grid, snake, food, obstacle, power-up, partikel, UI, webcam, menu, pause, game over. |
| `model_utils.py` | Validasi keberadaan model MediaPipe dan download otomatis jika belum tersedia. |
| `storage.py` | Load dan save data skor ke file JSON. |
| `README.md` | Dokumentasi utama project. |

## Detail Modul

### `snake_finger_control.py`

- Menampilkan informasi awal aplikasi.
- Mengecek dependency:
  - `pygame`
  - `cv2`
  - `mediapipe`
  - `numpy`
- Mengecek versi MediaPipe.
- Menentukan lokasi model `hand_landmarker.task`.
- Memanggil `ensure_model`.
- Membuat instance `UpgradedGame`.
- Menjalankan game dengan `game.run()`.

### `config.py`

- Menyimpan ukuran layar dan grid.
- Menyimpan nilai FPS dan speed default.
- Menyimpan ukuran preview kamera.
- Menyimpan konfigurasi model MediaPipe.
- Menyimpan konstanta arah:
  - `RIGHT`
  - `LEFT`
  - `UP`
  - `DOWN`
- Menyimpan konstanta state:
  - `STATE_MENU`
  - `STATE_PLAYING`
  - `STATE_PAUSED`
  - `STATE_GAME_OVER`
- Menyimpan konstanta power-up:
  - `POWER_SLOW`
  - `POWER_DOUBLE`
  - `POWER_SHIELD`
  - `POWER_GHOST`
- Menyimpan definisi difficulty.
- Menyimpan koneksi skeleton tangan untuk rendering landmark.

### `game.py`

- Menginisialisasi Pygame.
- Menginisialisasi renderer.
- Menginisialisasi skor dari storage.
- Menginisialisasi `HandTracker`.
- Mengatur difficulty aktif.
- Mengatur state game.
- Memproses input keyboard.
- Memproses input gesture.
- Mengatur update snake, food, obstacle, power-up, dan particle.
- Menghitung speed aktif berdasarkan difficulty, level, dan efek slow.
- Mengaktifkan dan membersihkan efek power-up.
- Menyimpan skor saat game selesai.
- Mengatur semua proses render sesuai state.
- Membersihkan resource saat game ditutup.

### `entities.py`

- `Snake`
  - Menyimpan body ular.
  - Menyimpan arah gerak.
  - Menolak arah balik langsung.
  - Menggerakkan ular.
  - Mengecek tabrakan dengan badan atau obstacle.
  - Menambah panjang dan skor saat makan.
- `Food`
  - Menyimpan posisi makanan.
  - Respawn ke posisi valid.
  - Efek pulse.
- `PowerUp`
  - Memilih jenis power-up acak.
  - Respawn ke posisi valid.
  - Menyimpan warna dan label.
  - Efek pulse.
- `Particle`
  - Menyimpan posisi, velocity, warna, dan lifetime.
  - Update posisi dan fade lifetime.
- `make_particle_burst`
  - Membuat kumpulan partikel dari posisi grid.

### `hand_tracker.py`

- Membuka webcam.
- Membuat MediaPipe HandLandmarker.
- Menjalankan tracking di thread terpisah.
- Membaca frame kamera secara real-time.
- Flip frame agar gerakan terasa natural.
- Mengubah frame ke RGB untuk MediaPipe.
- Mengambil landmark tangan.
- Menggambar skeleton tangan.
- Mengambil posisi ujung jari telunjuk.
- Menghitung delta posisi jari untuk menentukan arah.
- Menggunakan `GestureRecognizer` untuk klasifikasi gesture.
- Menyediakan method thread-safe:
  - `get_direction`
  - `get_gesture`
  - `get_status_label`
  - `get_cam_frame`
  - `stop`

### `gestures.py`

- Mengklasifikasikan gesture berdasarkan posisi ujung jari dan PIP joint.
- Gesture yang didukung:
  - `PALM`
  - `FIST`
  - `TWO_FINGERS`
- Mengembalikan `None` jika gesture tidak cocok.

### `renderer.py`

- Mengelola font Pygame.
- Menggambar grid.
- Menggambar snake.
- Menggambar mata ular.
- Menggambar food.
- Menggambar power-up.
- Menggambar obstacle.
- Menggambar particle.
- Menggambar score dan status level.
- Menggambar efek aktif.
- Menggambar preview kamera.
- Menggambar panel no-camera.
- Menggambar hint kontrol.
- Menggambar menu.
- Menggambar overlay pause.
- Menggambar overlay game over.

### `model_utils.py`

- Mengecek apakah file model sudah tersedia.
- Menampilkan ukuran model jika ditemukan.
- Mengunduh model dari URL MediaPipe jika belum ada.
- Menampilkan progress download.
- Menampilkan solusi manual jika download gagal.

### `storage.py`

- Menyediakan default struktur skor.
- Membaca skor dari JSON.
- Menggabungkan data skor yang ditemukan dengan default.
- Menyimpan skor ke JSON.
- Menangani error baca/tulis agar game tidak langsung crash.

## File Runtime yang Dibutuhkan

Beberapa file dapat muncul atau dibutuhkan saat runtime:

| File | Keterangan |
| --- | --- |
| `scores.json` | File skor lokal, dibuat/diperbarui saat game over. |
| `hand_landmarker.task` | Model MediaPipe untuk deteksi tangan. |

## Catatan

- Berdasarkan struktur kode saat ini, project sudah dibuat modular.
- Pembagian modul sudah cukup jelas antara konfigurasi, entity, game controller, rendering, tracking tangan, utilitas model, dan storage.
- File `snake-learn.zip` ada di folder project, tetapi bukan bagian langsung dari runtime game Python.
