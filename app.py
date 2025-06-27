import streamlit as st
import lyricsgenius
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# -- Streamlit Config
st.set_page_config(page_title="🎤 Taylor Swift Lyrics Visualizer", layout="centered")
st.title("🎶 Sing with Streamlit: Taylor Swift Lyrics Visualizer")
st.markdown("Enter a **Taylor Swift** song title to get the lyrics and a word cloud.")

# -- Check if Genius API token is loaded
try:
    GENIUS_API_TOKEN = st.secrets["GENIUS_API_TOKEN"]
    st.success("✅ Genius API token loaded successfully.")
    st.caption(f"🔑 Token begins with: `{GENIUS_API_TOKEN[:4]}...{GENIUS_API_TOKEN[-4:]}`")
except KeyError:
    st.error("❌ Genius API token not found in st.secrets. Please add it in your deployment settings.")
    st.stop()

# -- Initialize Genius API
genius = lyricsgenius.Genius(
    GENIUS_API_TOKEN,
    skip_non_songs=True,
    excluded_terms=["(Remix)", "(Live)"],
    remove_section_headers=True
)

# -- Helper: Clean Lyrics
def clean_lyrics(lyrics):
    lyrics = re.sub(r"\[.*?\]", "", lyrics)  # Remove [Verse], [Chorus], etc.
    lines = [line.strip() for line in lyrics.splitlines() if line.strip()]
    return "\n".join(lines)

# -- Input field
song_title = st.text_input("🎵 Song Title", placeholder="e.g., Love Story")

if song_title:
    with st.spinner("Fetching lyrics..."):
        try:
            song = genius.search_song(song_title, artist="Taylor Swift")
            if song and song.lyrics:
                cleaned_lyrics = clean_lyrics(song.lyrics)

                st.subheader("🎧 Clean Lyrics")
                st.text_area("Lyrics", value=cleaned_lyrics, height=300)

                st.subheader("☁️ Word Cloud")
                wordcloud = WordCloud(width=800, height=400, background_color="white").generate(cleaned_lyrics)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
            else:
                st.error("No lyrics found for this song.")
        except Exception as e:
            st.error("❌ An error occurred while fetching lyrics.")
            st.exception(e)
