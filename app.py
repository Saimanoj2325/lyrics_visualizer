import streamlit as st
import requests
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

# -- Sample themes for word cloud
def get_sample_lyrics_for_wordcloud(song_title):
    themes = {
        'love story': 'love story romeo juliet princess dream marry forever tale kiss',
        'shake it off': 'shake haters break dance play music move bounce beat shine',
        'blank space': 'blank space name insane magic madness love heartbreak game cherry lips',
        'anti-hero': 'anti hero problems midnight thoughts mirror flaws strange lonely real',
        'enchanted': 'enchanted tonight sparkle fairy blushing wonder spell music stars magic',
        'all too well': 'autumn scarf wind dancing kitchen memories pain remember heartbreak',
        'cardigan': 'cardigan vintage soft safe scent warmth memories waves stars',
        'willow': 'willow flowing dancing spell golden dream river faith bound',
        'lover': 'lover forever heart home warm kiss vow magic calm',
        'delicate': 'delicate mystery secrets paper hands dive silence feel reputation'
    }

    for key, value in themes.items():
        if key in song_title.lower():
            return value
    return 'love music dancing heart memories forever young broken sparkle magic night'

# -- Generate word cloud
def generate_wordcloud(text):
    if not text.strip():
        return None
    return WordCloud(width=800, height=400, background_color="white").generate(text)

# -- Streamlit UI
st.set_page_config(page_title="🎤 Taylor Swift Lyrics Visualizer", layout="centered")
st.title("🎶 Taylor Swift Lyrics Visualizer")
st.markdown("Enter a **Taylor Swift** song title to see a themed word cloud.")

song_title = st.text_input("🎵 Song Title", placeholder="e.g., Love Story")

if song_title:
    with st.spinner("🔍 Fetching song info..."):
        song_data = search_song(song_title)

        if song_data:
            song_url = song_data["url"]
            st.markdown(f"🔗 [View on Genius]({song_url})")

            # Use theme-based text for word cloud
            themed_text = get_sample_lyrics_for_wordcloud(song_title)

            st.subheader("☁️ Word Cloud")
            wordcloud = generate_wordcloud(themed_text)
            if wordcloud:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
            else:
                st.warning("⚠️ Could not generate word cloud.")
        else:
            st.error("❌ Song not found.")
