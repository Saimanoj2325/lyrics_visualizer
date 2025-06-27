import streamlit as st
import requests
import lyricsgenius
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# -- Load Genius API token from Streamlit secrets
def get_genius_access_token():
    try:
        return st.secrets["GENIUS_API_TOKEN"]
    except KeyError:
        return None

# -- Search for song metadata using Genius API
def search_song(song_title, artist="Taylor Swift"):
    access_token = get_genius_access_token()
    if not access_token:
        st.error("Please add your Genius API access token in Streamlit Secrets!")
        return None

    base_url = "https://api.genius.com"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"q": f"{song_title} {artist}"}

    try:
        response = requests.get(f"{base_url}/search", headers=headers, params=params)
        response.raise_for_status()
        hits = response.json()["response"]["hits"]
        for hit in hits:
            if artist.lower() in hit["result"]["primary_artist"]["name"].lower():
                return hit["result"]
        return hits[0]["result"] if hits else None
    except Exception as e:
        st.error(f"Error fetching song metadata: {e}")
        return None

# -- Get lyrics using lyricsgenius
def fetch_lyrics(song_title, artist="Taylor Swift"):
    try:
        token = get_genius_access_token()
        genius = lyricsgenius.Genius(token, skip_non_songs=True, remove_section_headers=True)
        genius.verbose = False  # hide logs
        song = genius.search_song(song_title, artist=artist)
        if song and song.lyrics:
            return song.lyrics
        else:
            return None
    except Exception as e:
        st.error(f"Lyrics fetch failed: {e}")
        return None

# -- Clean the lyrics for word cloud
def clean_lyrics(lyrics):
    lyrics = re.sub(r"\[.*?\]", "", lyrics)  # Remove [Verse], etc.
    lines = [line.strip() for line in lyrics.splitlines() if line.strip()]
    return "\n".join(lines)

# -- Streamlit UI
st.set_page_config(page_title="🎤 Taylor Swift Lyrics Visualizer", layout="centered")
st.title("🎶 Sing with Streamlit: Taylor Swift Lyrics Visualizer")
st.markdown("Enter a **Taylor Swift** song title to get the lyrics and a word cloud.")

song_title = st.text_input("🎵 Song Title", placeholder="e.g., Love Story")

if song_title:
    with st.spinner("🔍 Searching..."):
        song_data = search_song(song_title)

        if song_data:
            song_url = song_data["url"]
            st.markdown(f"[🔗 View on Genius]({song_url})")

            lyrics = fetch_lyrics(song_title)

            if lyrics:
                cleaned_lyrics = clean_lyrics(lyrics)

                if cleaned_lyrics.strip():
                    st.subheader("🎧 Clean Lyrics")
                    st.text_area("Lyrics", value=cleaned_lyrics, height=300)

                    st.subheader("☁️ Word Cloud")
                    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(cleaned_lyrics)
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation="bilinear")
                    ax.axis("off")
                    st.pyplot(fig)
                else:
                    st.warning("Lyrics are empty after cleaning.")
            else:
                st.error("❌ Could not fetch lyrics.")
        else:
            st.error("❌ Song not found.")
