import subprocess
import os
from pathlib import Path

class AudioIngester:
    """Handles the ingestion and standardization of audio/video files."""
    
    def __init__(self, target_sr=16000, channels=1):
        self.target_sr = target_sr
        self.channels = channels

    def convert_to_standard_wav(self, input_path: str, output_path: str):
        """
        Uses FFmpeg to convert any input into 16kHz mono PCM WAV.
        -ar: Sets sampling rate to 16000 Hz
        -ac: Sets audio channels to 1 (mono)
        -acodec: Sets codec to pcm_s16le (standard 16-bit)
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Command construction as a list for subprocess safety
        command =[
            r"D:\Code\ffmpeg-8.1-essentials_build\bin\ffmpeg.exe",
            "-i", str(input_path),      # read the input file from input_path
            "-ar", str(self.target_sr), # resample audio to target sample_path
            '-ac', str(self.channels),  # Mono channel
            '-acodec', 'pcm_s16le',     # 16-bit PCM codec
            '-y',                       # Overwrite output if exists
            str(output_path)
        ]

        try:
            # Run the command and capture output for error handling
            result = subprocess.run(
                command, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, 
                text=True, 
                check=True
            )
            print(f"Successfully converted: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg Error: {e.stderr}")
            raise RuntimeError("FFmpeg conversion failed.") from e
        except FileNotFoundError:
            raise RuntimeError("FFmpeg is not installed on your system.")