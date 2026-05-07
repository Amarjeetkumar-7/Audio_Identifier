import os
import sys
import subprocess


def separate_audio_stems(input_file, output_dir):
    print(f"Separating: {input_file}...")

    input_file = os.path.abspath(input_file)
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    cmd = [
        sys.executable, "-m", "demucs",
        "-n", "htdemucs",
        "--device", "cpu",
        "-o", output_dir,
        input_file
    ]

    print(f"  Using Python: {sys.executable}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("Demucs error:", result.stderr[-2000:])
        return None

    # Demucs output path: output_dir/htdemucs/<base_name>/<stem>.wav
    demucs_out = os.path.join(output_dir, "htdemucs", base_name)

    stems = {}
    for name in ["vocals", "drums", "bass", "other"]:
        src = os.path.join(demucs_out, f"{name}.wav")
        if os.path.exists(src):
            stems[name] = src
            print(f"  ✓ {name}: {src}")
        else:
            print(f"  ✗ {name} not found at {src}")

    if not stems:
        print("No stems generated.")
        return None

    print(f"✓ 4 stems saved in: {demucs_out}")
    return stems
