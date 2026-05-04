import os
import librosa
import numpy as np
import soundfile as sf


def separate_audio_stems(input_file, output_dir):
    """Separates audio into two stems using Librosa HPS/S decomposition."""
    print(f"Separating: {input_file}...")

    os.makedirs(output_dir, exist_ok=True)

    # Load audio in mono at the file's native sample rate
    y, sr = librosa.load(input_file, sr=None, mono=True)

    # Harmonic/Percussive source separation
    harmonic, percussive = librosa.effects.hpss(y)

    base_name = os.path.splitext(os.path.basename(input_file))[0]
    result_dir = os.path.join(output_dir, base_name)
    os.makedirs(result_dir, exist_ok=True)

    vocals_path = os.path.join(result_dir, "vocals.wav")
    background_path = os.path.join(result_dir, "background.wav")

    # Save the separated tracks
    sf.write(vocals_path, harmonic, sr)
    sf.write(background_path, percussive, sr)

    return {
        "vocals": vocals_path,
        "background": background_path
    }

# Example Usage:
# stems = separate_audio_stems('data/processed/input_16k.wav', 'data/stems/')
# print(f"Isolated Background SFX/Music at: {stems['background']}")
