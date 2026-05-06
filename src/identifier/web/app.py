import os
import asyncio
from flask import Flask, render_template, request
from identifier.ingestion import AudioIngester
from identifier.recognition import MusicIdentifier

app = Flask(__name__, template_folder='../templates')
app.secret_key = "iitg_project_secret"

# Initialize modular classes
ingester = AudioIngester()
music_id = MusicIdentifier()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])  # FIX: Added
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    upload_folder = "uploads"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # os.path.join highlight will disappear now that methods= is fixed
    upload_path = os.path.join(upload_folder, file.filename)
    file.save(upload_path)

    standard_wav = os.path.join(upload_folder, "temp_processing.wav")
    ingester.convert_to_standard_wav(upload_path, standard_wav)

    # loop highlight will disappear now that the function scope is valid

    loop = None
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        music_result = loop.run_until_complete(music_id.identify_clip(standard_wav))
    finally:
            if loop is not None:
                loop.close()

    sfx_result = {
        "labels":[],  # FIX: Added empty list
        "source": "Freesound.org"
    }

    result = {
        "music": music_result,
        "sfx": sfx_result
    }

    if os.path.exists(standard_wav): os.remove(standard_wav)
    if os.path.exists(upload_path): os.remove(upload_path)
    
    return render_template('index.html', result=result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)