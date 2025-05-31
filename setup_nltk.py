import nltk


def setup_nltk():
    try:
        nltk.data.find('tokenizers/punkt')
        print("[INFO] NLTK 'punkt' tokenizer is already installed.")
    except LookupError:
        print("[INFO] Downloading NLTK 'punkt' tokenizer...")
        nltk.download('punkt')
        print("[INFO] Download complete.")


if __name__ == "__main__":
    setup_nltk()
