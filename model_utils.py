import os
import urllib.request

from config import MODEL_FILENAME, MODEL_URL


def ensure_model(model_path: str) -> bool:
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"Model ditemukan: {model_path} ({size_mb:.1f} MB)")
        return True

    print("\nModel MediaPipe belum ada, mendownload...")
    print(f"   File : {MODEL_FILENAME}")
    print(f"   URL  : {MODEL_URL}")
    print("   Size : ~5 MB, harap tunggu...\n")

    try:
        def _progress(count, block_size, total_size):
            if total_size > 0:
                pct = int(count * block_size * 100 / total_size)
                print(f"\r   Progress: {min(pct, 100)}%", end="", flush=True)

        urllib.request.urlretrieve(MODEL_URL, model_path, reporthook=_progress)
        print(f"\nBerhasil didownload: {model_path}")
        return True
    except Exception as e:
        print(f"\nGagal download model: {e}")
        print("\n   Solusi: Download manual dari link berikut:")
        print(f"   {MODEL_URL}")
        print(f"   Simpan sebagai '{MODEL_FILENAME}' di folder yang sama dengan script ini.")
        return False
