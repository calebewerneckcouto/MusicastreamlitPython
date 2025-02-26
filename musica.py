import os
from pathlib import Path
import streamlit as st
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch

# Constantes do projeto
DOWNLOADS_FOLDER = "downloads"

def setup_ffmpeg():
    """
    Configura o caminho correto do FFmpeg.
    
    Retorna:
        str: Caminho absoluto para o executável do FFmpeg
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_locations = [
        os.path.join(current_dir, "ffmpeg", "bin"),
        os.path.join(current_dir, "ffmpeg", "bin", "ffmpeg.exe"),  
        os.getenv('FFMPEG_PATH', None)
    ]
    
    for location in ffmpeg_locations:
        if location and os.path.exists(location):
            return location
    
    raise FileNotFoundError("FFmpeg não encontrado!")

def search_youtube(query):
    """
    Busca um vídeo no YouTube.
    
    Args:
        query (str): Termo de busca
        
    Returns:
        str: URL do vídeo encontrado ou None se não encontrar
    """
    search = VideosSearch(query, limit=1)
    results = search.result()
    return results['result'][0]['link'] if results['result'] else None

def download_audio(url):
    """
    Baixa o áudio de um vídeo do YouTube.
    
    Args:
        url (str): URL do vídeo
        
    Returns:
        str: Caminho do arquivo MP3 baixado ou None em caso de erro
    """
    try:
        ffmpeg_path = setup_ffmpeg()
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': ffmpeg_path,
            'outtmpl': os.path.join(DOWNLOADS_FOLDER, '%(title)s.%(ext)s')
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = os.path.join(DOWNLOADS_FOLDER, f"{info['title']}.mp3")
            return filename
            
    except Exception as e:
        st.error(f"Erro ao baixar o áudio: {str(e)}")
        return None

def main():
    """
    Função principal do aplicativo Streamlit.
    """
    os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)
    
    st.title("CWCDEV YouTube MP3 Downloader")
    music_name = st.text_input("Digite o nome da música:")
    
    if st.button("Baixar Música"):
        if music_name:
            st.write("🔎 Procurando no YouTube...")
            
            try:
                video_url = search_youtube(music_name)
                
                if video_url:
                    st.write(f"🎵 Vídeo encontrado: [Clique para assistir]({video_url})")
                    st.write("⬇ Baixando áudio...")
                    
                    audio_file = download_audio(video_url)
                    
                    if audio_file and os.path.exists(audio_file):
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
            except Exception as e:
                st.error(f"Ocorreu um erro: {str(e)}")
        else:
            st.warning("Por favor, insira um nome de música.")

if __name__ == "__main__":
    main()