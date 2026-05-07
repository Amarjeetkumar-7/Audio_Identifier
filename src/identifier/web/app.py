import sys
import os

# ── Fix Python path so 'identifier' package is found ──────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_DIR  = os.path.join(BASE_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import asyncio
import uuid
import multiprocessing
multiprocessing.freeze_support()

import streamlit as st

# ── MUST be first Streamlit command ───────────────────────────────
st.set_page_config(
    page_title="Audio Identifier",
    page_icon="🎵",
    layout="centered"
)

# ── Lazy imports with error display ───────────────────────────────
try:
    from identifier.ingestion import AudioIngester
except Exception as e:
    st.error(f"❌ Failed to import AudioIngester: {e}")
    st.stop()

try:
    from identifier.recognition import MusicIdentifier
except Exception as e:
    st.error(f"❌ Failed to import MusicIdentifier: {e}")
    st.stop()

try:
    from identifier.separator import separate_audio_stems
except Exception as e:
    st.error(f"❌ Failed to import separate_audio_stems: {e}")
    st.stop()

# ── Paths ──────────────────────────────────────────────────────────
UPLOAD_FOLDER = os.path.join(BASE_DIR, "src", "identifier", "uploads")
STEMS_FOLDER  = os.path.join(BASE_DIR, "src", "identifier", "stems")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STEMS_FOLDER,  exist_ok=True)

# ── Cached model loading ───────────────────────────────────────────
@st.cache_resource
def load_models():
    ingester = AudioIngester()
    music_id  = MusicIdentifier()
    return ingester, music_id

ingester, music_id = load_models()

# ── UI ─────────────────────────────────────────────────────────────
st.title("🎵 Audio Identifier")
st.markdown("Upload an audio file to **identify the song** and **separate its stems**.")

uploaded_file = st.file_uploader(
    "Choose an audio file",
    type=["mp3", "wav", "flac", "ogg", "m4a"]
)

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/mp3")

    if st.button("🔍 Identify & Separate", use_container_width=True):

        unique_id    = uuid.uuid4().hex[:8]
        original_ext = os.path.splitext(uploaded_file.name)[1]
        saved_name   = f"{unique_id}{original_ext}"
        upload_path  = os.path.join(UPLOAD_FOLDER, saved_name)
        standard_wav = os.path.join(UPLOAD_FOLDER, f"{unique_id}_processed.wav")

        with open(upload_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # ── Step 1: Ingestion ──────────────────────────────────────
        with st.spinner("⚙️ Processing audio..."):
            try:
                ingester.convert_to_standard_wav(upload_path, standard_wav)
                st.success("✅ Audio processed!")
            except Exception as e:
                st.error(f"❌ Ingestion failed: {e}")
                st.stop()

        # ── Step 2: Separation ─────────────────────────────────────
        stems = None
        with st.spinner("🎼 Separating stems (this may take a minute)..."):
            try:
                stems = separate_audio_stems(standard_wav, STEMS_FOLDER)

                # Fix: fallback to htdemucs subdir if paths don't exist
                if stems:
                    base_name    = os.path.splitext(os.path.basename(standard_wav))[0]
                    fallback_dir = os.path.join(STEMS_FOLDER, "htdemucs", base_name)
                    fixed_stems  = {}
                    for stem_name, stem_path in stems.items():
                        if os.path.exists(stem_path):
                            fixed_stems[stem_name] = stem_path
                        else:
                            fallback_path = os.path.join(fallback_dir, f"{stem_name}.wav")
                            if os.path.exists(fallback_path):
                                fixed_stems[stem_name] = fallback_path
                    stems = fixed_stems if fixed_stems else None

                if stems:
                    st.success("✅ Stems separated!")
                else:
                    st.warning("⚠️ Stems not found after separation.")

            except Exception as e:
                st.warning(f"⚠️ Stem separation failed: {e}")

        # ── Step 3: Recognition ────────────────────────────────────
        music_result = {}
        with st.spinner("🔎 Identifying song..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                if stems and "other" in stems:
                    recognition_file = stems["other"]
                elif stems and "vocals" in stems:
                    recognition_file = stems["vocals"]
                else:
                    recognition_file = standard_wav

                music_result = loop.run_until_complete(
                    music_id.identify_clip(recognition_file)
                )
                loop.close()
            except Exception as e:
                st.warning(f"⚠️ Recognition failed: {e}")

        # ── Cleanup ────────────────────────────────────────────────
        for path in [upload_path, standard_wav]:
            if os.path.exists(path):
                os.remove(path)

        # ── Results: Song Info ─────────────────────────────────────
        st.divider()
        st.subheader("🎤 Song Identification")

        if music_result and "error" not in music_result:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🎵 Title",  music_result.get("title",  "Unknown"))
                st.metric("👤 Artist", music_result.get("artist", "Unknown"))
            with col2:
                st.metric("💿 Album",  music_result.get("album",  "Unknown"))
                st.metric("📅 Year",   music_result.get("year",   "Unknown"))
            if music_result.get("genre"):
                st.info(f"🎸 Genre: {music_result.get('genre')}")
            if music_result.get("links"):
                st.markdown("**🔗 Listen On:**")
                for service, url in music_result["links"].items():
                    if url:
                        st.markdown(f"- [{service.capitalize()}]({url})")
        else:
            st.warning("Could not identify the song.")
            if music_result.get("error"):
                st.code(music_result["error"])

        # ── Results: Stems ─────────────────────────────────────────
        if stems:
            st.divider()
            st.subheader("🎛️ Separated Stems")
            stem_icons = {
                "vocals": "🎤",
                "drums":  "🥁",
                "bass":   "🎸",
                "other":  "🎹"
            }
            cols = st.columns(2)
            for i, (stem_name, stem_path) in enumerate(stems.items()):
                icon = stem_icons.get(stem_name, "🔊")
                with cols[i % 2]:
                    st.markdown(f"**{icon} {stem_name.capitalize()}**")
                    if os.path.exists(stem_path):
                        with open(stem_path, "rb") as audio_file:
                            st.audio(audio_file.read(), format="audio/wav")
                    else:
                        st.warning(f"File not found: {stem_path}")
