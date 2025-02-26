import os
from pathlib import Path
import streamlit as st
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch
from pydub import AudioSegment
import tempfile
import logging

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constantes do projeto
DOWNLOADS_FOLDER = "downloads"

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

def sanitize_filename(filename):
    """
    Limpa o nome do arquivo removendo caracteres especiais e limitando o tamanho.
    """
    # Remove caracteres especiais e limita o tamanho do nome
    safe_filename = ''.join(c for c in filename if c.isalnum() or c in '-_ .')
    # Limita o tamanho do nome do arquivo
    if len(safe_filename) > 100:
        safe_filename = safe_filename[:100]
    return safe_filename

def download_audio(url):
    """
    Baixa o áudio de um vídeo do YouTube usando pydub.
    """
    try:
        # Baixa o arquivo temporário
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(tempfile.gettempdir(), '%(title)s.%(ext)s')
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            temp_file = ydl.prepare_filename(info)
            
            # Sanitiza o título para o nome do arquivo final
            safe_title = sanitize_filename(info['title'])
            wav_file = os.path.join(DOWNLOADS_FOLDER, f"{safe_title}.wav")
            
            # Converte para WAV usando pydub
            audio = AudioSegment.from_file(temp_file)
            audio.export(wav_file, format="wav")
            
            # Remove arquivo temporário
            os.remove(temp_file)
            return wav_file
            
    except Exception as e:
        st.error(f"Erro ao baixar o áudio: {str(e)}")
        return None

def main():
    """
    Função principal do aplicativo Streamlit.
    """
    os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)
    st.title("CWCDEV YouTube WAV Downloader")
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
                                label="🎵 Download WAV",
                                data=file,
                                file_name=os.path.basename(audio_file),
                                mime="audio/wav"
                            )
                    else:
                        st.error("Erro ao baixar o áudio.")
                else:
                    st.error("Nenhum vídeo encontrado.")
            except Exception as e:
                logger.error(f"Erro no processamento: {str(e)}")
                st.error(f"Ocorreu um erro: {str(e)}")
        else:
            st.warning("Por favor, insira um nome de música.")

if __name__ == "__main__":
    main()