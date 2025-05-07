"""
Configurações centralizadas para a aplicação.
"""

import os
import torch

# Diretório base da aplicação
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Diretório de logs
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Configurações de vídeo
VIDEO_SETTINGS = {
    'silence_threshold': -53,
    'min_silence_len': 4000,
    'silence_padding': -1200,
    'video_codec': 'libx264',
    'audio_codec': 'aac',
    'preset': 'ultrafast',
    'threads': 12,
    'device': 'cuda' if torch.cuda.is_available() else 'cpu'

}

# Configurações de extração de frames
FRAME_EXTRACTION = {
    'threshold': 5.0,
    'max_frames': 100,
    'default_interval': 180,
    'min_scene_length': 30
}

# Configurações de upscaling de imagens
UPSCALE_SETTINGS = {
    'model_name': 'RealESRGAN_x4plus.pth',
    'scale': 4
}

# Configurações de transcrição
TRANSCRIPTION_SETTINGS = {
    "model": "base",           # Modelo Whisper
    "language": "pt",        # Idioma padrão
    "threads": 12          # Número de threads para processamento
}
    
# Extensões suportadas
SUPPORTED_EXTENSIONS = {
    "video": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"],
    "audio": [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"],
    "image": [".jpg", ".jpeg", ".png", ".bmp", ".tiff"],
}
