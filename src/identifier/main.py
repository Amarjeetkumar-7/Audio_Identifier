import multiprocessing
multiprocessing.freeze_support()

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # suppress all TF/CUDA warnings

import asyncio
import warnings
warnings.filterwarnings("ignore")

from identifier.ingestion import AudioIngester
from identifier.recognition import MusicIdentifier
from identifier.separator import separate_audio_stems


async def run_identification(input_media):
    ingester = AudioIngester()
    temp_wav = "processed_audio.wav"

    try:
        ingester.convert_to_standard_wav(input_media, temp_wav)
        print(f"✓ Ingestion complete: {temp_wav}")
    except Exception as e:
        print(f"✗ Ingestion failed: {e}")
        return

    stems_dir = "stems"
    stems = separate_audio_stems(temp_wav, stems_dir)

    if not stems:
        print("✗ Separation failed.")
        return

    print("✓ Separation complete:")
    print(f"  Vocals:  {stems.get('vocals')}")
    print(f"  Drums:   {stems.get('drums')}")
    print(f"  Bass:    {stems.get('bass')}")
    print(f"  Other:   {stems.get('other')}")

    print("\n--- Identifying Music ---")
    recognizer = MusicIdentifier()

    recognition_file = stems.get("other") or stems.get("vocals") or temp_wav

    try:
        info = await recognizer.identify_clip(recognition_file)
    except Exception as e:
        info = {"error": str(e)}

    if "error" in info:
        print(f"Result: {info['error']}")
    else:
        print(f"Track: {info.get('title')}")
        print(f"Artist: {info.get('artist')}")
        links = info.get("links") or {}
        if links:
            print("Sources:")
            for service, url in links.items():
                print(f"  {service}: {url}")

    if os.path.exists(temp_wav):
        os.remove(temp_wav)


if __name__ == "__main__":
    asyncio.run(run_identification(r"D:\Audio\Cheques - song.mp3"))
