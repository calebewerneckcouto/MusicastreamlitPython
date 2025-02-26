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
DOWNLOADS_FOLDER = "/app/downloads"  # Caminho absoluto no servidor
TEMP_FOLDER = "/tmp/youtube_downloads"  # Pasta temporária para downloads

def setup_server():
    """Configura o ambiente do servidor"""
    try:
        # Criar diretórios necessários
        os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)
        os.makedirs(TEMP_FOLDER, exist_ok=True)
        
        # Configurar permissões
        os.chmod(DOWNLOADS_FOLDER, 0o775)
        os.chmod(TEMP_FOLDER, 0o775)
        
        # Verificar sistema operacional
        if os.name == 'nt':  # Windows
            logger.info("Executando no Windows")
        else:  # Unix/Linux
            if os.geteuid() == 0:
                logger.warning("Executando como root! Configure um usuário específico.")
        
        logger.info("Ambiente do servidor configurado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"Erro ao configurar servidor: {str(e)}")
        return False

def sanitize_filename(filename):
    """
    Limpa o nome do arquivo removendo caracteres especiais e limitando o tamanho.
    """
    safe_filename = ''.join(c for c in filename if c.isalnum() or c in '-_ .')
    if len(safe_filename) > 100:
        safe_filename = safe_filename[:100]
    return safe_filename

def download_audio(url):
    """
    Baixa o áudio de um vídeo do YouTube usando pydub.
    """
    try:
        # Configurações do yt-dlp
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
            
            # Sanitiza o título para o nome do arquivo final
            safe_title = sanitize_filename(info['title'])
            mp3_file = os.path.join(DOWNLOADS_FOLDER, f"{safe_title}.mp3")
            
            # Converte para MP3 usando pydub
            audio = AudioSegment.from_file(temp_file)
            audio.export(mp3_file, format="mp3")
            
            # Remove arquivo temporário
            os.remove(temp_file)
            return mp3_file
            
    except Exception as e:
        logger.error(f"Erro ao baixar o áudio: {str(e)}")
        st.error(f"Erro ao baixar o áudio: {str(e)}")
        return None

def main():
    """
    Função principal do aplicativo Streamlit.
    """
    # Configurar ambiente do servidor
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
                logger.error(f"Erro no processamento: {str(e)}")
                st.error(f"Ocorreu um erro: {str(e)}")
        else:
            st.warning("Por favor, insira um nome de música.")

if __name__ == "__main__":
    main()