import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# -- Load Genius API token from Streamlit secrets
def get_genius_access_token():
    try:
        return st.secrets["GENIUS_API_TOKEN"]
    except KeyError:
        return None

# -- Genius API Song Search
def search_song(song_title, artist="Taylor Swift"):
    access_token = get_genius_access_token()
    if not access_token:
        st.error("🚨 Add GENIUS_API_TOKEN in Streamlit secrets.")
        return None

    headers = {"Authorization": f"Bearer {access_token}"}
    search_url = "https://api.genius.com/search"
    params = {"q": f"{song_title} {artist}"}

    try:
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        hits = response.json()["response"]["hits"]
        for hit in hits:
            if artist.lower() in hit["result"]["primary_artist"]["name"].lower():
                return hit["result"]
        return hits[0]["result"] if hits else None
    except Exception as e:
        st.error(f"❌ Error searching song: {e}")
        return None

# -- Scrape lyrics from Genius song page
def fetch_lyrics_from_url(song_url):
    try:
        page = requests.get(song_url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(page.text, "html.parser")

        # Try new layout (React-based)
        lyrics_divs = soup.find_all("div", class_="Lyrics__Container")
        if lyrics_divs:
            lyrics = "\n".join([div.get_text(separator="\n") for div in lyrics_divs])
            return lyrics

        # Try fallback (old layout)
        lyrics_div = soup.find("div", class_="lyrics")
        if lyrics_div:
            return lyrics_div.get_text()

        return None
    except Exception as e:
        st.error(f"❌ Failed to scrape lyrics: {e}")
        return None

# -- Clean the lyrics
def clean_lyrics(lyrics):
    lyrics = re.sub(r"\[.*?\]", "", lyrics)  # Remove [Verse], etc.
    lines = [line.strip() for line in lyrics.splitlines() if line.strip()]
    return "\n".join(lines)

# -- Streamlit UI
st.set_page_config(page_title="🎤 Taylor Swift Lyrics Visualizer", layout="centered")
st.title("🎶 Taylor Swift Lyrics Visualizer")
st.markdown("Enter a **Taylor Swift** song title to get the lyrics and a word cloud.")

song_title = st.text_input("🎵 Song Title", placeholder="e.g., Love Story")

if song_title:
    with st.spinner("🔍 Fetching song info..."):
        song_data = search_song(song_title)

        if song_data:
            song_url = song_data["url"]
            st.markdown(f"🔗 [View on Genius]({song_url})")

            lyrics = fetch_lyrics_from_url(song_url)
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
                    st.warning("⚠️ Lyrics cleaned to empty — no word cloud.")
            else:
                st.error("❌ Couldn't extract lyrics from Genius page.")
        else:
            st.error("❌ Song not found.")
