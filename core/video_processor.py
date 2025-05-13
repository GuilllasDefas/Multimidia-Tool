"""
Módulo para processamento de vídeos, incluindo remoção de silêncio.
"""

import os
import time
from moviepy import VideoFileClip, concatenate_videoclips
from pydub import AudioSegment, silence
import tempfile

from config.settings import VIDEO_SETTINGS
from utils.logging_utils import (
    setup_logger,
    log_process_start,
    log_process_end,
)
from utils.file_utils import get_output_path

logger = setup_logger('video_processor')


class VideoProcessor:
    """Classe para processamento de vídeos."""

    def __init__(
        self, silence_thresh=None, min_silence_len=None, padding=None
    ):
        """
        Inicializa o processador de vídeo com os parâmetros especificados.

        Args:
            silence_thresh (int, optional): Limiar de silêncio em dB.
            min_silence_len (int, optional): Duração mínima do silêncio em ms.
            padding (int, optional): Tempo em ms adicionado antes e depois dos trechos com áudio.
        """
        self.silence_thresh = (
            silence_thresh or VIDEO_SETTINGS['silence_threshold']
        )
        self.min_silence_len = (
            min_silence_len or VIDEO_SETTINGS['min_silence_len']
        )
        self.padding = padding or VIDEO_SETTINGS['silence_padding']

    def remove_silence(self, video_input_path, video_output_path=None):
        """
        Remove automaticamente os silêncios de um vídeo.

        Args:
            video_input_path (str): Caminho do vídeo de entrada.
            video_output_path (str, optional): Caminho para salvar o vídeo sem silêncios.

        Returns:
            str: Caminho do vídeo processado.
        """
        if video_output_path is None:
            suffix = f' - Auto Edit - {self.silence_thresh} silence - {self.min_silence_len} minimo - pad {self.padding}'
            video_output_path = get_output_path(video_input_path, suffix)

        start_time = time.time()
        log_process_start(
            logger,
            'remover_silencios',
            input_path=video_input_path,
            output_path=video_output_path,
            silence_thresh=self.silence_thresh,
            min_silence_len=self.min_silence_len,
            padding=self.padding,
        )

        try:
            # Carrega o vídeo
            logger.info('Carregando o vídeo...')
            video = VideoFileClip(video_input_path)
            audio = video.audio

            # Extrai informações do vídeo original
            fps = video.fps
            resolution = video.size
            duration = video.duration
            logger.info(
                f'Parâmetros do vídeo original: FPS={fps}, Resolução={resolution}, Duração={duration:.2f}s'
            )

            # Extrai o áudio do vídeo
            logger.info('Extraindo o áudio do vídeo...')
            temp_audio_file = tempfile.NamedTemporaryFile(
                suffix='.wav', delete=False
            )
            audio.write_audiofile(
                temp_audio_file.name, codec='pcm_s16le', logger=None
            )

            # Carrega o áudio para análise
            logger.info('Carregando o áudio para análise...')
            audio_segment = AudioSegment.from_wav(temp_audio_file.name)

            # Detecta os silêncios
            logger.info('Detectando silêncios no áudio...')
            silent_ranges = silence.detect_silence(
                audio_segment,
                min_silence_len=self.min_silence_len,
                silence_thresh=self.silence_thresh,
            )

            # Processa os segmentos de áudio
            logger.info('Processando os segmentos de áudio...')
            silent_ranges = [
                (start - self.padding, end + self.padding)
                for start, end in silent_ranges
            ]
            silent_ranges = [
                (max(0, start), min(len(audio_segment), end))
                for start, end in silent_ranges
            ]

            # Identifica os segmentos com áudio
            audio_ranges = []
            prev_end = 0
            for start, end in silent_ranges:
                if prev_end < start:
                    audio_ranges.append((prev_end, start))
                prev_end = end
            if prev_end < len(audio_segment):
                audio_ranges.append((prev_end, len(audio_segment)))

            # Registra os cortes no log
            logger.info(f'Arquivo de entrada: {video_input_path}')
            for start, end in audio_ranges:
                duration = (end - start) / 1000.0
                logger.info(
                    f'Corte mantido: Início={start / 1000.0:.2f}s, Fim={end / 1000.0:.2f}s, Duração={duration:.2f}s'
                )

            # Cria os clipes de vídeo correspondentes aos segmentos com áudio
            logger.info(
                'Criando clipes de vídeo correspondentes aos segmentos com áudio...'
            )
            clips = [
                video.subclipped(start / 1000.0, end / 1000.0)
                for start, end in audio_ranges
            ]

            # Concatena os clipes e salva o vídeo final
            logger.info('Concatenando os clipes de vídeo...')
            final_video = concatenate_videoclips(clips)

            logger.info(f'Salvando o vídeo final em: {video_output_path}')
            final_video.write_videofile(
                video_output_path,
                codec=VIDEO_SETTINGS['video_codec'],
                audio_codec=VIDEO_SETTINGS['audio_codec'],
                fps=fps,
                preset=VIDEO_SETTINGS['preset'],
                threads=VIDEO_SETTINGS['threads'],
                logger=None,
            )

            # Limpa recursos
            logger.info('Removendo arquivo de áudio temporário...')
            audio.close()  # Fecha o áudio para liberar o arquivo temporário
            temp_audio_file.close()  # Fecha o arquivo temporário explicitamente
            os.remove(temp_audio_file.name)  # Remove o arquivo temporário

            end_time = time.time()
            duration = end_time - start_time
            log_process_end(logger, 'remover_silencios', duration)

            return video_output_path

        except Exception as e:
            logger.error(f'Erro ao remover silêncios: {str(e)}', exc_info=True)
            raise
