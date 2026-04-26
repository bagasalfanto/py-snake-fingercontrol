# 🐍 Snake Game - Finger Gesture Control

Game Snake klasik dengan kontrol menggunakan **gesture jari tangan** melalui webcam.

Gunakan **jari telunjuk Anda** untuk mengontrol gerakan ular secara real-time dengan MediaPipe Hand Detection.

---

## 🎮 Fitur Utama

✨ **Gesture Control**

- Gerakkan jari telunjuk ke **Kanan/Kiri/Atas/Bawah** untuk mengontrol ular
- Threshold adaptif untuk menghindari noise gerakan
- Fallback ke keyboard (WASD) jika webcam tidak terdeteksi

🤖 **MediaPipe Hand Tracking (Tasks API v0.10+)**

- Deteksi tangan real-time dengan akurasi tinggi
- Skeleton hand visualization (tulang tangan tampak di layar)
- Running mode VIDEO untuk tracking smooth antar frame

🎨 **Visual Polish**

- Grid-based playground
- Animasi ular dengan shading gradient
- Partikel efek saat makan makanan
- Preview webcam live di corner game
- UI score real-time

🔄 **Gameplay**

- Semakin panjang semakin cepat
- Makanan muncul random
- Collision detection dengan dinding dan badan sendiri
- Restart dan quit command

---

## 📋 Requirements

| Komponen               | Versi Minimum                  |
| ---------------------- | ------------------------------ |
| Python                 | >= 3.10                        |
| pygame-ce              | >= 2.5                         |
| mediapipe              | >= 0.10.x                      |
| opencv-python-headless | >= 4.x                         |
| numpy                  | >= 1.20                        |
| Webcam                 | Diperlukan (USB atau built-in) |

### ⚠️ Catatan Penting

- **Gunakan `pygame-ce`** (Community Edition), BUKAN `pygame` biasa
- **MediaPipe >= 0.10** menggunakan Tasks API baru (tanpa `.solutions`)
- Model `hand_landmarker.task` akan **otomatis didownload** (~5 MB) saat pertama kali
- Kompatibel dengan Python 3.10, 3.11, 3.12, 3.13, 3.14+

---

## 🚀 Instalasi

### 1. Persiapan Environment (Opsional tapi Recommended)

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan
# Pada Windows:
venv\Scripts\activate
# Pada macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# SANGAT PENTING: Uninstall pygame biasa (jika ada)
pip uninstall pygame -y

# Install dependencies yang diperlukan
pip install pygame-ce opencv-python-headless mediapipe numpy
```

### 3. Jalankan Game

```bash
python snake_finger_control.py
```

**Pada jalankan pertama:**

- Script akan otomatis **download model MediaPipe** (~5 MB)
- Tunggu hingga muncul pesan ✅ "Model ditemukan"
- Game akan terbuka dengan preview webcam

---

## 🎮 Cara Bermain

### Kontrol Ular

| Input                   | Aksi                                  |
| ----------------------- | ------------------------------------- |
| 🖐️ **Geser Jari Kanan** | Ular bergerak ke KANAN                |
| 🖐️ **Geser Jari Kiri**  | Ular bergerak ke KIRI                 |
| 🖐️ **Geser Jari Atas**  | Ular bergerak ke ATAS                 |
| 🖐️ **Geser Jari Bawah** | Ular bergerak ke BAWAH                |
| ⌨️ **W/A/S/D**          | Fallback keyboard (jika webcam error) |
| ⌨️ **R**                | Restart game                          |
| ⌨️ **Q**                | Quit game                             |

### Tips Bermain

- 🎯 **Posisikan tangan** di depan webcam dengan jarak ~20-50 cm
- 👆 **Gunakan jari telunjuk** (jari yang paling stabil untuk tracking)
- 💨 **Gerakan cepat dan jelas** untuk responsif maksimal
- 📱 **Jangan kurangi cahaya** — pastikan lighting baik
- 🚀 **Semakin lama survival** = semakin cepat ular bergerak

---

## ⚙️ Konfigurasi (Opsional)

Edit bagian **KONSTANTA & KONFIGURASI** di `snake_finger_control.py`:

```python
SCREEN_W, SCREEN_H  = 800, 600        # Ukuran layar
CELL_SIZE           = 20               # Ukuran grid cell
SNAKE_SPEED         = 8                # Update speed ular (frame)
FINGER_THRESHOLD    = 25               # Min pixel delta untuk trigger arah baru
CAM_W, CAM_H        = 200, 150        # Ukuran preview webcam
FPS                 = 60               # Frame rate game
```

---

## 🐛 Troubleshooting

### ❌ "Webcam tidak ditemukan!"

**Solusi:**

1. Pastikan webcam sudah tersambung dan aktif
2. Cek di Windows Settings → Privacy → Camera (izin aplikasi)
3. Gunakan keyboard (WASD) sebagai fallback
4. Restart aplikasi

### ❌ "RuntimeError: There is no current event loop in thread 'MainThread'" (Python 3.14+ Windows)

**Solusi:** Script sudah handle otomatis, tapi jika masih error:

```python
# Tambahkan di main() sebelum menjalankan game:
import asyncio
if sys.platform == "win32":
    asyncio.set_event_loop(asyncio.new_event_loop())
```

### ❌ "Gesture tidak responsif / lag"

**Penyebab & Solusi:**

- ✅ Pencahayaan kurang → Tingkatkan cahaya di sekitar
- ✅ Threshold terlalu tinggi → Kurangi `FINGER_THRESHOLD` ke 15-20
- ✅ Webcam resolution rendah → Update driver atau gunakan USB camera
- ✅ Gerakan terlalu lambat → Gerak jari lebih cepat dan jelas

### ❌ "ModuleNotFoundError: No module named 'pygame'"

**Solusi:**

```bash
pip uninstall pygame -y
pip install pygame-ce
```

### ❌ Model tidak bisa download otomatis

**Solusi Manual:**

1. Download dari: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
2. Rename menjadi `hand_landmarker.task`
3. Simpan di **folder yang sama** dengan script `snake_finger_control.py`
4. Jalankan ulang

---

## 📊 Struktur Code

```
snake_finger_control.py
├── Konstanta & Warna            (baris 1-60)
├── Helper (Download Model)       (baris 61-100)
├── Class HandTracker            (baris 101-250)
│   └── Thread OpenCV + MediaPipe (Gesture Detection)
├── Class Game                    (baris 251-400)
│   ├── Grid & Snake State
│   ├── Food Spawn & Collision
│   └── Render & Score
└── Main Loop                     (baris 400+)
    ├── Event Handling
    ├── Gesture Input
    ├── Game Update
    └── Render
```

---

## 🔬 Technical Details

### Deteksi Gerakan

- **Algoritma:** Hitung delta posisi jari telunjuk antar frame
- **Threshold:** Gerakan harus minimal `FINGER_THRESHOLD` px untuk trigger arah baru
- **Dominance:** Ambil komponen (X/Y) yang paling dominan

### Thread Model

```
Thread 1 (Background):
  Webcam Input → MediaPipe Detection → Gesture Compute → Update Shared State

Thread 2 (Main - Pygame):
  Get Direction → Game Logic → Render → Display
  (Protected by Lock untuk synchronization)
```

### MediaPipe Tasks API (v0.10+)

- **Mode:** VIDEO (memerlukan timestamp monotonic)
- **Input:** `mp.Image` (RGB)
- **Output:** `HandLandmarkerResult` (21 landmarks per tangan)
- **No `.solutions` API** — gunakan `vision.HandLandmarker` langsung

---

## 📝 License

Free to use & modify. Enjoy! 🎮

---

## 🤝 Kontribusi

Punya ide atau bug report?

- Pastikan webcam working
- Test dengan minimal 3 gestures berbeda
- Report dengan versi Python & OS Anda

---

**Happy Gaming! 🐍✨**
