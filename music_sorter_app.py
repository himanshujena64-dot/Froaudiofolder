"""
music_sorter_app.py — upload a batch of music files you've downloaded from
Pixabay (or anywhere), and auto-sort them into your app's music/<mood>/
folders based on filename keywords. You confirm/override each guess before
anything is saved, so nothing gets misfiled silently.

RUN:
    pip install streamlit
    streamlit run music_sorter_app.py

WORKFLOW:
1. Download a batch of tracks from Pixabay Music normally (browser, one by
   one or a few tabs at once) into your Downloads folder.
2. Open this app, drag the whole batch in at once.
3. For each file, the app guesses a mood from the filename (Pixabay
   filenames are usually descriptive, e.g. "sad-emotional-piano-12345.mp3").
   Confirm or change the dropdown per file.
5. Click "Sort & Save All" — it copies every file straight into
   music/<mood>/ next to this script (or wherever you point --out).
"""

import os
import re
import shutil
import streamlit as st

MOODS = [
    "upbeat", "dramatic", "calm", "inspirational", "suspense",
    "sad", "romantic", "epic", "energetic", "nostalgic",
]

# Keywords used to guess mood from filename / uploaded title text.
# Extend these freely — more keywords = better auto-guessing.
MOOD_KEYWORDS = {
    "upbeat":        ["upbeat", "happy", "fun", "pop", "cheerful", "bright", "playful"],
    "dramatic":      ["dramatic", "tension", "drama", "intense", "orchestral"],
    "calm":          ["calm", "peaceful", "relax", "ambient", "soft", "gentle", "meditation"],
    "inspirational": ["inspir", "motivat", "uplift", "hopeful", "triumph"],
    "suspense":      ["suspense", "mystery", "thriller", "dark", "eerie"],
    "sad":           ["sad", "melanchol", "emotional", "sorrow", "heartbreak"],
    "romantic":      ["romantic", "love", "sentimental", "tender"],
    "epic":          ["epic", "trailer", "powerful", "cinematic", "heroic"],
    "energetic":     ["energetic", "driving", "action", "sport", "electronic", "beat"],
    "nostalgic":     ["nostalgic", "memories", "vintage", "warm", "retro"],
}


def guess_mood(filename: str) -> str | None:
    name = filename.lower()
    scores = {m: 0 for m in MOODS}
    for mood, kws in MOOD_KEYWORDS.items():
        for kw in kws:
            if kw in name:
                scores[mood] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


st.set_page_config(page_title="Music Sorter", page_icon="🎵")
st.title("🎵 Music Sorter")
st.caption("Upload a batch of downloaded tracks — auto-sorts into mood folders.")

out_dir = st.text_input("Output folder (your app's music/ folder)", value="./music")

uploaded = st.file_uploader(
    "Drop your downloaded music files here (you can select many at once)",
    type=["mp3", "wav", "m4a"],
    accept_multiple_files=True,
)

if uploaded:
    st.subheader(f"{len(uploaded)} file(s) — confirm mood for each")
    decisions = {}

    for f in uploaded:
        guessed = guess_mood(f.name)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.audio(f, format="audio/mp3")
            st.caption(f.name)
        with col2:
            default_idx = MOODS.index(guessed) if guessed else 0
            choice = st.selectbox(
                "Mood",
                MOODS,
                index=default_idx,
                key=f"mood_{f.name}",
                label_visibility="collapsed",
            )
            if guessed is None:
                st.caption("⚠️ no guess — pick manually")
        decisions[f.name] = (f, choice)

    st.divider()
    if st.button("✅ Sort & Save All", type="primary"):
        saved = 0
        for fname, (fileobj, mood) in decisions.items():
            mood_dir = os.path.join(out_dir, mood)
            os.makedirs(mood_dir, exist_ok=True)
            dest = os.path.join(mood_dir, fname)
            fileobj.seek(0)
            with open(dest, "wb") as out:
                shutil.copyfileobj(fileobj, out)
            saved += 1
        st.success(f"Saved {saved} file(s) into their mood folders under '{out_dir}'.")
else:
    st.info("Waiting for files — drag and drop your downloaded batch above.")
