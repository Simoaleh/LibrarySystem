"""Run everything in one command: setup, seed, then start the server."""
import subprocess
import sys


def nltk_ready():
    try:
        import nltk
        nltk.data.find("corpora/stopwords")
        nltk.data.find("sentiment/vader_lexicon")
        nltk.data.find("tokenizers/punkt")
        return True
    except Exception:
        return False


def setup():
    print("[1/3] Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

    print("[2/3] Downloading NLTK corpora...")
    if not nltk_ready():
        code = "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
        subprocess.run([sys.executable, "-c", code], check=True)
    else:
        print("    NLTK corpora already present — skipping.")


def seed():
    print("[3/3] Seeding the database...")
    subprocess.run([sys.executable, "seed.py"], check=True)


def launch():
    print("Starting server at http://127.0.0.1:5000 (Ctrl+C to stop)")
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    if "--no-install" not in sys.argv:
        setup()
    else:
        print("Skipping install (--no-install).")
    if "--no-seed" not in sys.argv:
        seed()
    else:
        print("Skipping seed (--no-seed).")
    launch()
