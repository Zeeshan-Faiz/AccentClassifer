import torchaudio
import torch.nn.functional as F
from speechbrain.pretrained import SpeakerRecognition

# Set the proper audio backend for Windows
torchaudio.set_audio_backend("soundfile")


def classify_accent(test_audio_path, ref_embeddings):
    """
    Classify the accent of a given test .wav file.

    Args:
        test_audio_path (str): Path to test .wav file
        ref_embeddings (dict): {accent: avg_embedding}

    Returns:
        dict: {
            "predicted_accent": str,
            "scores": {accent: similarity_score},
            "confidence": float (0-100)
        }
    """
    # Load ECAPA model
    verification = SpeakerRecognition.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        savedir="pretrained_models/ecapa"
    )

    # Load and normalize test audio
    signal, fs = torchaudio.load(test_audio_path)
    if fs != 16000:
        signal = torchaudio.transforms.Resample(fs, 16000)(signal)

    # Extract test embedding
    test_embedding = verification.encode_batch(signal).squeeze(0).squeeze(0)

    # Compare with references
    scores = {}
    for accent, ref_emb in ref_embeddings.items():
        sim = F.cosine_similarity(test_embedding, ref_emb, dim=0).item()
        scores[accent] = sim

    # Predict top accent
    predicted_accent = max(scores, key=scores.get)
    confidence = scores[predicted_accent] * 100

    return {
        "predicted_accent": predicted_accent,
        "scores": scores,
        "confidence": round(confidence, 2)
    }
