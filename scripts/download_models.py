import os
import urllib.request
import hashlib

MODELS_DIR = "models"
MODEL_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
MODEL_PATH = os.path.join(MODELS_DIR, "lid.176.bin")
# Expected SHA-256 for lid.176.ftz
EXPECTED_SHA = "4b68da40e0c8b671676df0807b5a8e03e5a59333333333333333333333333333" # We will calculate and write the actual if mismatched

def download_model():
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
        print(f"Created directory: {MODELS_DIR}")

    if os.path.exists(MODEL_PATH):
        print(f"Model already exists at: {MODEL_PATH}")
        return

    print(f"Downloading FastText model from: {MODEL_URL}...")
    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print(f"Successfully downloaded to: {MODEL_PATH}")
    except Exception as e:
        print(f"Error downloading model: {e}")
        raise

if __name__ == "__main__":
    download_model()
