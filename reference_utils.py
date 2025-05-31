import os
import torch
import torchaudio
from speechbrain.pretrained import SpeakerRecognition

# Set the proper audio backend for Windows
torchaudio.set_audio_backend("soundfile")


def get_reference_embeddings(refs_dir="refs"):
    """
    Extract averaged ECAPA embeddings for each accent directory inside `refs/`.

    Returns:
        dict: {accent_name: embedding_tensor}
    """
    # Load ECAPA-TDNN model from SpeechBrain
    print("[INFO] Loading ECAPA-TDNN model...")
    verification = SpeakerRecognition.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        savedir="pretrained_models/ecapa"
    )

    accent_embeddings = {}

    for accent_folder in os.listdir(refs_dir):
        accent_path = os.path.join(refs_dir, accent_folder)
        if not os.path.isdir(accent_path):
            continue

        embeddings = []

        for wav_file in os.listdir(accent_path):
            if not wav_file.endswith(".wav"):
                continue

            wav_path = os.path.join(accent_path, wav_file)
            print(f"[INFO] Processing {wav_path}")

            # Load audio
            signal, fs = torchaudio.load(wav_path)
            if fs != 16000:
                signal = torchaudio.transforms.Resample(fs, 16000)(signal)

            # Extract embedding
            embedding = verification.encode_batch(signal).squeeze(0).squeeze(0)  # shape: [1, 192]
            embeddings.append(embedding)

        # Average embeddings for this accent
        if embeddings:
            accent_embeddings[accent_folder] = torch.stack(embeddings).mean(dim=0)
            print(f"[INFO] Stored averaged embedding for {accent_folder}")

    return accent_embeddings
