import sys
import os
import asyncio
import warnings
warnings.filterwarnings("ignore")

from identifier.ingestion import AudioIngester
from identifier.recognition import MusicIdentifier
from processing.separator import separate_audio_stems

async def run_identification(input_media):
    # Ingestion: Convert to standardized WAV
    ingester = AudioIngester()
    input_media = r"D:\Export\hatt thari.mp4"
    temp_wav = "processed_audio.wav"
    ingester.convert_to_standard_wav(input_media, temp_wav)
    print(f"✓ Ingestion complete: {temp_wav}")

    # Separation: split the converted WAV into two stems
    stems_dir = "stems"
    stems = separate_audio_stems(temp_wav, stems_dir)
    print(f"✓ Separation complete:")
    print(f"  vocals: {stems['vocals']}")
    print(f"  background: {stems['background']}")

    # Recognition: identify music from the background stem
    print(f"\n--- Identifying Music ---")
    
    recognizer = MusicIdentifier()
    info = await recognizer.identify_clip(stems['background'])
    
    if "error" in info:
        print(f"Result: {info['error']}")
    else:
        print(f"Track: {info['title']}")
        print(f"Artist: {info['artist']}")
        print("Sources:")
        links = info.get('links') or {}
        for service, url in links.items():
            print(f"  {service}: {url}")
        if not links:
            print("  (no sources available)")

if __name__ == "__main__":
    asyncio.run(run_identification("sample_clip.mp4"))

