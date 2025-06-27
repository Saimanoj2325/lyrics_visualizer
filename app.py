import streamlit as st
import lyricsgenius
import requests
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# -- Helper: Get Genius client with custom headers
def get_genius_client():
    try:
        token = st.secrets["GENIUS_API_TOKEN"]
        session = requests.Session()
        session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        genius = lyricsgenius.Genius(
            token,
            skip_non_songs=True,
            excluded_terms=["(Remix)", "(Live)"],
            remove_section_headers=True,
            timeout=15,
            retries=3,
            verbose=False
        )
        genius._session = session
        return genius
    except KeyError:
        st.error("🚫 Genius API token not found in Streamlit secrets.")
        return None

# -- Helper: Clean Lyrics
def clean_lyrics(lyrics):
    lyrics = re.sub(r"\[.*?\]", "", lyrics)  # Remove [Verse], [Chorus], etc.
    lines = [line.strip() for line in lyrics.splitlines() if line.strip()]
    return "\n".join(lines)

# -- Streamlit UI
st.set_page_config(page_title="🎤 Taylor Swift Lyrics Visualizer", layout="centered")
st.title("🎶 Sing with Streamlit: Taylor Swift Lyrics Visualizer")
st.markdown("Enter a **Taylor Swift** song title to get the lyrics and a word cloud.")

song_title = st.text_input("🎵 Song Title", placeholder="e.g., Love Story")

if song_title:
    genius = get_genius_client()
    if genius:
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
                    st.warning("🤷 Could not fetch lyrics. Try another song or check spelling.")
            except Exception as e:
                st.error(f"⚠️ An error occurred while fetching lyrics: {e}")
