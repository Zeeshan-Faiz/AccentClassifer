from audio_extract import extract_audio_from_video
from reference_utils import get_reference_embeddings
from accent_classification import classify_accent
from langdetect import detect, LangDetectException
from functools import lru_cache
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# For transcription & language detection - using OpenAI Whisper via whisper package
import whisper

import nltk

nltk.download('punkt')
try:
    nltk.download('punkt_tab')
except:
    print("punkt_tab not available but continuing...")

# Initialize Whisper ASR model once
model = whisper.load_model("base")  # or "small", "medium" depending on resources


def transcribe_audio(audio_path):
    """
    Transcribe audio using Whisper ASR.
    Returns the transcript as a string.
    """
    result = model.transcribe(audio_path)
    return result["text"]


def is_english_transcript(transcript):
    try:
        return detect(transcript) == 'en'
    except LangDetectException:
        return False


def generate_summary(transcript):
    parser = PlaintextParser.from_string(transcript, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 3)  # top 3 sentences

    return " ".join(str(sentence) for sentence in summary)


# Cache embeddings to avoid recomputing
REF_EMBEDDINGS = None


@lru_cache(maxsize=1)
def load_reference_embeddings():
    global REF_EMBEDDINGS
    if REF_EMBEDDINGS is None:
        REF_EMBEDDINGS = get_reference_embeddings("refs")
    return REF_EMBEDDINGS


def process_video(video_url):

    # Step 1: Extract audio
    audio_path = extract_audio_from_video(video_url)

    # Step 2: Transcribe and check English
    transcript = transcribe_audio(audio_path)
    if not transcript.strip():
        return {"error": "Transcription returned empty text."}
    if not is_english_transcript(transcript):
        return {"error": "English not detected in audio transcript. Cannot classify accent."}

    # Step 3: Load reference embeddings (cached)
    ref_embeddings = load_reference_embeddings()

    # Step 4: Classify accent
    results = classify_accent(audio_path, ref_embeddings)

    # Step 5: Generate summary
    summary = generate_summary(transcript)

    # Return all results in a dict
    return {
        "accent": results['predicted_accent'],
        "confidence": results['confidence'],
        "summary": summary,
        "transcript": transcript
    }
