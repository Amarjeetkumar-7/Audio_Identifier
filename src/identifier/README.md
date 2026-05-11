## Creating a tool which identify the sound and SFX used in a clip

# Audio Identifier
Term project for DA377 – Term-Project 1 in the B.Sc. (Hons.) Data Science & AI (Online) programme at IIT Guwahati.
The project implements a small local pipeline that:

Standardizes an input media file to WAV

Separates it into stems (vocals, drums, bass, other)

Identifies the song using Shazam via shazamio

# Features
Ingestion – converts any supported audio/video into 16 kHz mono PCM WAV using FFmpeg (AudioIngester).

Stem separation – runs Demucs (htdemucs model) from the CLI to produce four stems (separate_audio_stems).

Music recognition – calls Shazam through the shazamio library and extracts title, artist, album, year, and links (MusicIdentifier).

End‑to‑end script – main.py wires everything together using asyncio.run, prints simple progress messages, and cleans up temporary files.




# Project structure
identifier/ingestion.py – FFmpeg‑based WAV conversion.

identifier/separator.py – Demucs‑based stem separation.

identifier/recognition.py – Shazamio‑based music identification.

main.py – orchestration, example entry point.

# Running the demo
Place a test audio file on your system.

Update the path in main.py:

python
if __name__ == "__main__":
    asyncio.run(run_identification(r"D:\Audio\Cheques - song.mp3"))
Run:

bash
python main.py
You should see logs for ingestion, stem generation, and the recognized track information printed in the terminal

# Dependencies
Main dependencies used in the project:

Python (tested with Python 3.x)

FFmpeg – required for audio conversion in ingestion.py; must be installed and accessible at the path configured in the code.

Demucs – used for audio source separation (CLI access via python -m demucs).

shazamio – asynchronous Shazam client for music recognition.

Standard library modules: os, sys, subprocess, asyncio, warnings, multiprocessing, pathlib.

Other Python packages may be required transitively by Demucs (e.g., PyTorch/torchaudio) and by shazamio, and should be installed via pip as per their documentation.

# Setup and installation (example)
These steps are indicative; exact versions can be adjusted based on the environment.

Clone the repository

bash
git clone <your-repo-url>
cd <your-repo-folder>
Create a virtual environment (recommended)

bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
Install Python dependencies

bash
pip install -r requirements.txt
The requirements.txt should include at least shazamio and any libraries required by Demucs. Demucs itself can be installed via pip install demucs or following the official setup guide.

Install FFmpeg

FFmpeg must be installed separately and the ffmpeg executable path should match the location used in AudioIngester.convert_to_standard_wav (currently hard‑coded in ingestion.py).

# Design choices and limitations
The project is designed for local experimentation, not for heavy batch processing or deployment at scale.

The recognition relies on Shazam’s backend via an unofficial client (shazamio), so network connectivity is required and behaviour may depend on Shazam’s API changes.

Demucs stem separation on CPU can be computationally expensive and may be slow on low‑end machines.

Error handling is basic but explicit: the code prints simple messages and returns None or an "error" field when steps fail, allowing the user to see where the pipeline stopped.


# Acknowledgements
Demucs for music source separation models.

Shazamio for providing a Python interface to Shazam’s recognition service.

FFmpeg for reliable audio format conversion.





