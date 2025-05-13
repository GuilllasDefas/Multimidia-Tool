"""
Módulo para transcrição de áudio/vídeo para texto.
"""

import os
import time
import torch
import whisper
import datetime
from moviepy import VideoFileClip

from config.settings import TRANSCRIPTION_SETTINGS
from utils.logging_utils import (
    setup_logger,
    log_process_start,
    log_process_end,
)
from utils.file_utils import (
    get_output_path,
    create_temp_file,
    is_supported_file,
)

logger = setup_logger('transcriber')


class Transcriber:
    """Classe para transcrição de áudio/vídeo para texto."""

    def __init__(self, model_name=None, language=None):
        """
        Inicializa o transcritor com o modelo e idioma especificados.

        Args:
            model_name (str, optional): Nome do modelo Whisper a ser usado.
            language (str, optional): Código do idioma para transcrição.
        """
        self.model_name = model_name or TRANSCRIPTION_SETTINGS['model']
        self.language = language or TRANSCRIPTION_SETTINGS['language']
        self.model = None
        self.device = None

    def load_model(self):
        """
        Carrega o modelo Whisper para transcrição.

        Returns:
            tuple: (modelo, device) - O modelo carregado e o dispositivo usado.
        """
        if self.model is not None:
            return self.model, self.device

        log_process_start(logger, 'load_model', model_name=self.model_name)

        try:
            # Determinar o dispositivo a ser usado
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f'Usando dispositivo: {self.device}')

            # Carregar o modelo
            logger.info(f"Carregando modelo Whisper '{self.model_name}'...")
            self.model = whisper.load_model(
                self.model_name, device=self.device
            )

            log_process_end(logger, 'load_model')
            return self.model, self.device

        except Exception as e:
            logger.error(f'Erro ao carregar modelo: {str(e)}', exc_info=True)
            raise

    def extract_audio(self, video_path, audio_out=None):
        """
        Extrai o áudio de um arquivo de vídeo.

        Args:
            video_path (str): Caminho do arquivo de vídeo.
            audio_out (str, optional): Caminho para salvar o áudio extraído.

        Returns:
            str: Caminho do arquivo de áudio extraído.
        """
        if audio_out is None:
            audio_out = create_temp_file(suffix='.wav')

        log_process_start(
            logger, 'extract_audio', video_path=video_path, audio_out=audio_out
        )

        try:
            logger.info(f'Extraindo áudio do vídeo: {video_path}')
            clip = VideoFileClip(video_path)
            clip.audio.write_audiofile(
                audio_out, codec='pcm_s16le', logger=None
            )
            clip.close()

            log_process_end(logger, 'extract_audio')
            return audio_out

        except Exception as e:
            logger.error(f'Erro ao extrair áudio: {str(e)}', exc_info=True)
            raise

    def format_timestamp(self, seconds):
        """
        Formata segundos para o formato de timestamp do SRT (HH:MM:SS,mmm).

        Args:
            seconds (float): Tempo em segundos.

        Returns:
            str: Timestamp formatado.
        """
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        return (
            f'{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}'
        )

    def create_srt(self, segments, output_path):
        """
        Cria um arquivo de legenda no formato SRT.

        Args:
            segments (list): Lista de segmentos de transcrição.
            output_path (str): Caminho para salvar o arquivo SRT.

        Returns:
            str: Caminho do arquivo SRT.
        """
        srt_path = os.path.splitext(output_path)[0] + '.srt'

        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments):
                # Escrever número do segmento
                f.write(f'{i+1}\n')

                # Escrever timestamps
                start_time = self.format_timestamp(segment['start'])
                end_time = self.format_timestamp(segment['end'])
                f.write(f'{start_time} --> {end_time}\n')

                # Escrever texto
                f.write(f"{segment['text'].strip()}\n\n")

        logger.info(f'Arquivo de legendas SRT criado em: {srt_path}')
        return srt_path

    def transcribe(self, input_path, output_path=None):
        """
        Transcreve um arquivo de áudio ou vídeo para texto.

        Args:
            input_path (str): Caminho do arquivo de entrada (áudio ou vídeo).
            output_path (str, optional): Caminho para salvar o texto transcrito.

        Returns:
            tuple: (output_path, srt_path, text) - Caminho do arquivo de texto, arquivo SRT e o texto transcrito.
        """
        if output_path is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = get_output_path(
                input_path, f'_transcricao_{timestamp}', '.txt'
            )

        log_process_start(
            logger,
            'transcribe',
            input_path=input_path,
            output_path=output_path,
            model=self.model_name,
            language=self.language,
        )

        try:
            audio_path = None
            is_temp = False

            # Verificar se é áudio ou vídeo
            if is_supported_file(input_path, 'video'):
                logger.info(
                    'Arquivo de entrada é um vídeo, extraindo áudio...'
                )
                audio_path = create_temp_file(suffix='.wav')
                self.extract_audio(input_path, audio_path)
                is_temp = True
            elif is_supported_file(input_path, 'audio'):
                logger.info('Arquivo de entrada é um áudio.')
                audio_path = input_path
            else:
                raise ValueError(
                    f'Formato de arquivo não suportado: {input_path}'
                )

            # Carregar o modelo se ainda não foi carregado
            model, device = self.load_model()

            # Realizar a transcrição
            logger.info('Iniciando transcrição...')
            inicio = time.time()
            resultado = model.transcribe(
                audio_path,
                language=self.language,
                fp16=(device == 'cuda'),
                verbose=False,
            )
            duracao = time.time() - inicio
            logger.info(f'Transcrição concluída em {duracao:.2f} segundos.')

            texto = resultado.get('text')
            if not texto:
                logger.warning('A transcrição não produziu texto.')

            # Salvar o texto transcrito
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(texto)
            logger.info(f'Transcrição salva em: {output_path}')

            # Criar arquivo de legendas SRT
            segmentos = resultado.get('segments', [])
            srt_path = self.create_srt(segmentos, output_path)

            # Limpar arquivo temporário se necessário
            if is_temp and audio_path and os.path.exists(audio_path):
                logger.info(f'Removendo arquivo temporário: {audio_path}')
                os.remove(audio_path)

            log_process_end(logger, 'transcribe', duracao)
            return output_path, srt_path, texto

        except Exception as e:
            logger.error(
                f'Erro durante a transcrição: {str(e)}', exc_info=True
            )
            raise
