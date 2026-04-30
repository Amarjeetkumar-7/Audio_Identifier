import sys
import os

from identifier.ingestion import AudioIngester

if __name__ == "__main__":
    ingester = AudioIngester()
    # Replace with your actual sample path
    ingester.convert_to_standard_wav(r"D:\Export\hatt thari.mp4", "processed_audio.wav")