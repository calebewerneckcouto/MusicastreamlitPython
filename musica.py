import streamlit as st
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch
import os

# Definir caminho para downloads
DOWNLOADS_FOLDER = "downloads"
os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

def search_youtube(query):
    search = VideosSearch(query, limit=1)
    results = search.result()
    if results['result']:
        return results['result'][0]['link']
    return None

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': r'C:\ffmpeg\bin',  # Certifique-se de que o ffmpeg está neste caminho
        'outtmpl': os.path.join(DOWNLOADS_FOLDER, '%(title)s.%(ext)s')
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = os.path.join(DOWNLOADS_FOLDER, f"{info['title']}.mp3")  # Nome do arquivo MP3
            return filename
    except Exception as e:
        st.error(f"Erro ao baixar o áudio: {str(e)}")
        return None

st.title("CWCDEV YouTube MP3 Downloader")

music_name = st.text_input("Digite o nome da música:")

if st.button("Baixar Música"):
    if music_name:
        st.write("🔎 Procurando no YouTube...")
        video_url = search_youtube(music_name)
        
        if video_url:
            st.write(f"🎵 Vídeo encontrado: [Clique para assistir]({video_url})")
            st.write("⬇ Baixando áudio...")
            audio_file = download_audio(video_url)
            
            if audio_file and os.path.exists(audio_file):
                # Abre o arquivo para download
                with open(audio_file, "rb") as file:
                    st.download_button(
                        label="🎶 Download MP3",
                        data=file,
                        file_name=os.path.basename(audio_file),
                        mime="audio/mpeg"
                    )
            else:
                st.error("Erro ao baixar o áudio.")
        else:
            st.error("Nenhum vídeo encontrado.")
    else:
        st.warning("Por favor, insira um nome de música.")
