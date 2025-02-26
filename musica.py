import os
from pathlib import Path
import streamlit as st
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch
from pydub import AudioSegment
import tempfile
import logging
import threading
from queue import Queue

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constantes do projeto
DOWNLOADS_FOLDER = "/app/downloads"
TEMP_FOLDER = "/tmp/youtube_downloads"

def setup_server():
    """Configura o ambiente do servidor"""
    try:
        os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)
        os.makedirs(TEMP_FOLDER, exist_ok=True)
        os.chmod(DOWNLOADS_FOLDER, 0o775)
        os.chmod(TEMP_FOLDER, 0o775)
        logger.info("Ambiente do servidor configurado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"Erro ao configurar servidor: {str(e)}")
        return False

def sanitize_filename(filename):
    """Limpa o nome do arquivo removendo caracteres especiais e limitando o tamanho."""
    safe_filename = ''.join(c for c in filename if c.isalnum() or c in '-_ .')
    if len(safe_filename) > 100:
        safe_filename = safe_filename[:100]
    return safe_filename

def download_audio(url, queue):
    """Baixa o áudio em uma thread separada e retorna o resultado via queue."""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(TEMP_FOLDER, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'nocheckcertificate': True,
            'prefer_free_formats': True
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            temp_file = ydl.prepare_filename(info)
            
            safe_title = sanitize_filename(info['title'])
            mp3_file = os.path.join(DOWNLOADS_FOLDER, f"{safe_title}.mp3")
            
            audio = AudioSegment.from_file(temp_file)
            audio.export(mp3_file, format="mp3")
            os.remove(temp_file)
            
            queue.put(('success', mp3_file))
    except Exception as e:
        logger.error(f"Erro ao baixar o áudio: {str(e)}")
        queue.put(('error', str(e)))

def main():
    """Função principal do aplicativo Streamlit."""
    if not setup_server():
        logger.error("Falha na configuração do servidor!")
        return
    
    st.title("CWCDEV YouTube MP3 Downloader")
    music_name = st.text_input("Digite o nome da música:")
    
    if st.button("Baixar Música"):
        if music_name:
            st.write("🔎 Procurando no YouTube...")
            try:
                video_url = VideosSearch(query=music_name, limit=1).result()['result'][0]['link']
                if video_url:
                    st.write(f"🎵 Vídeo encontrado: [Clique para assistir]({video_url})")
                    st.write("⬇ Baixando áudio...")
                    
                    # Criar uma queue para comunicação entre threads
                    queue = Queue()
                    
                    # Iniciar download em thread separada
                    thread = threading.Thread(
                        target=download_audio,
                        args=(video_url, queue),
                        daemon=True
                    )
                    thread.start()
                    
                    # Aguardar resultado com timeout
                    thread.join(timeout=60)
                    
                    if not thread.is_alive():
                        result, data = queue.get()
                        if result == 'success':
                            with open(data, "rb") as file:
                                st.download_button(
                                    label="🎶 Download MP3",
                                    data=file,
                                    file_name=os.path.basename(data),
                                    mime="audio/mpeg"
                                )
                        else:
                            st.error(f"Erro ao baixar o áudio: {data}")
                    else:
                        st.error("Tempo limite excedido!")
                else:
                    st.error("Nenhum vídeo encontrado.")
            except Exception as e:
                logger.error(f"Erro no processamento: {str(e)}")
                st.error(f"Ocorreu um erro: {str(e)}")
        else:
            st.warning("Por favor, insira um nome de música.")

if __name__ == "__main__":
    main()