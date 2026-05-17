import os
import sys

from config import MODEL_FILENAME
from game import UpgradedGame
from model_utils import ensure_model


def check_dependencies() -> bool:
    print("\nMengecek dependencies...")
    errors = []
    for pkg, install_cmd in [
        ("pygame", "pip uninstall pygame -y && pip install pygame-ce"),
        ("cv2", "pip install opencv-python-headless"),
        ("mediapipe", "pip install mediapipe"),
        ("numpy", "pip install numpy"),
    ]:
        try:
            __import__(pkg)
            print(f"   OK {pkg}")
        except ImportError:
            print(f"   MISSING {pkg} -> {install_cmd}")
            errors.append(pkg)

    if errors:
        print("\nJalankan perintah install di atas lalu coba lagi.")
        return False
    return True


def main():
    print("=" * 60)
    print("  SNAKE GAME - FINGER GESTURE CONTROL")
    print("  pygame-ce + opencv-python-headless + mediapipe")
    print("=" * 60)

    if not check_dependencies():
        sys.exit(1)

    import mediapipe as mp
    print(f"\n   MediaPipe versi: {getattr(mp, '__version__', '?')}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, MODEL_FILENAME)
    if not ensure_model(model_path):
        print("\nGame tidak dapat dijalankan tanpa model MediaPipe.")
        sys.exit(1)

    print("\nMemulai game...")
    game = UpgradedGame(model_path)
    game.run()


if __name__ == "__main__":
    main()
