"""
Módulo para extração de frames-chave de vídeos.
"""

import os
import cv2
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector, ThresholdDetector
from scenedetect.scene_manager import save_images

from config.settings import FRAME_EXTRACTION
from utils.logging_utils import setup_logger, log_process_start, log_process_end
from utils.file_utils import ensure_dir_exists

logger = setup_logger("frame_extractor")

class FrameExtractor:
    """Classe para extração de frames de vídeos."""
    
    def __init__(self, threshold=None, max_frames=None):
        """
        Inicializa o extrator de frames com os parâmetros especificados.
        
        Args:
            threshold (float, optional): Limiar para detecção de cenas.
            max_frames (int, optional): Número máximo aproximado de frames desejado.
        """
        self.threshold = threshold or FRAME_EXTRACTION['threshold']
        self.max_frames = max_frames or FRAME_EXTRACTION['max_frames']
    
    def extract_keyframes(self, video_path, output_dir=None, usar_threshold_detector=False):
        """
        Extrai frames-chave de um vídeo usando detecção de cenas.
        
        Args:
            video_path (str): Caminho para o arquivo de vídeo.
            output_dir (str, optional): Diretório onde os frames serão salvos.
            usar_threshold_detector (bool, optional): Se True, usa ThresholdDetector em vez de ContentDetector.
            
        Returns:
            str: Diretório onde os frames foram salvos.
        """
        if output_dir is None:
            base_dir = os.path.dirname(video_path)
            output_dir = os.path.join(base_dir, "keyframes_extraidos")
        
        output_dir = ensure_dir_exists(output_dir)
        
        log_process_start(logger, "extract_keyframes", 
                        video_path=video_path, 
                        output_dir=output_dir,
                        threshold=self.threshold,
                        usar_threshold_detector=usar_threshold_detector)

        try:
            logger.info("Abrindo o vídeo...")
            video = open_video(video_path)
            
            scene_manager = SceneManager()
            
            # Escolher o detector com base no parâmetro
            if usar_threshold_detector:
                logger.info(f"Usando ThresholdDetector com threshold={self.threshold}")
                scene_manager.add_detector(ThresholdDetector(threshold=self.threshold))
            else:
                logger.info(f"Usando ContentDetector com threshold={self.threshold}")
                scene_manager.add_detector(ContentDetector(threshold=self.threshold))
            
            logger.info("Detectando cenas... Isso pode levar algum tempo para vídeos longos.")
            scene_manager.detect_scenes(video=video, show_progress=True)
            
            lista_cenas = scene_manager.get_scene_list()
            num_cenas = len(lista_cenas)
            logger.info(f"Número de cenas detectadas: {num_cenas}")
            
            if num_cenas == 0:
                logger.info("Nenhuma cena detectada. Usando método de extração por intervalos regulares como fallback.")
                self.extract_regular_frames(video_path, output_dir)
                return output_dir
            
            logger.info(f"Salvando 1 keyframe por cena detectada...")
            save_images(
                scene_list=lista_cenas,
                video=video,
                num_images=1,
                output_dir=output_dir,
                image_name_template='$SCENE_NUMBER',
                show_progress=True
            )
            logger.info(f"Total de {num_cenas} frames salvos em '{output_dir}'.")
            
            log_process_end(logger, "extract_keyframes")
            return output_dir
            
        except Exception as e:
            logger.error(f"Erro ao extrair keyframes: {str(e)}", exc_info=True)
            raise
    
    def extract_regular_frames(self, video_path, output_dir=None, intervalo=None):
        """
        Extrai frames em intervalos regulares de um vídeo.
        
        Args:
            video_path (str): Caminho para o arquivo de vídeo.
            output_dir (str, optional): Diretório onde os frames serão salvos.
            intervalo (int, optional): Intervalo de frames para salvar.
            
        Returns:
            str: Diretório onde os frames foram salvos.
        """
        if output_dir is None:
            base_dir = os.path.dirname(video_path)
            output_dir = os.path.join(base_dir, "frames_regulares")
        
        output_dir = ensure_dir_exists(output_dir)
        intervalo = intervalo or FRAME_EXTRACTION['default_interval']
        
        log_process_start(logger, "extract_regular_frames", 
                         video_path=video_path, 
                         output_dir=output_dir,
                         intervalo=intervalo)
        
        try:
            logger.info(f"Salvando frames regulares do vídeo: {video_path}")
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Não foi possível abrir o vídeo {video_path}")
                raise ValueError(f"Não foi possível abrir o vídeo {video_path}")
            
            frame_count = 0
            saved_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % intervalo == 0:
                    frame_path = os.path.join(output_dir, f"frame_{frame_count:06d}.jpg")
                    cv2.imwrite(frame_path, frame)
                    saved_count += 1
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Frames regulares salvos: {saved_count} frames em '{output_dir}'.")
            
            log_process_end(logger, "extract_regular_frames")
            return output_dir
            
        except Exception as e:
            logger.error(f"Erro ao extrair frames regulares: {str(e)}", exc_info=True)
            raise
    
    def detect_scenes_by_diff(self, video_path, output_dir=None, diff_threshold=None, min_scene_length=None):
        """
        Detecta cenas com base em diferenças de quadros consecutivos usando OpenCV.
        
        Args:
            video_path (str): Caminho para o arquivo de vídeo.
            output_dir (str, optional): Pasta onde os frames das cenas serão salvos.
            diff_threshold (int, optional): Limiar para considerar uma diferença significativa entre quadros.
            min_scene_length (int, optional): Número mínimo de quadros para considerar uma nova cena.
            
        Returns:
            str: Diretório onde os frames foram salvos.
        """
        if output_dir is None:
            base_dir = os.path.dirname(video_path)
            output_dir = os.path.join(base_dir, "cenas_detectadas")
        
        output_dir = ensure_dir_exists(output_dir)
        diff_threshold = diff_threshold or 30  # Valor padrão
        min_scene_length = min_scene_length or FRAME_EXTRACTION['min_scene_length']
        
        log_process_start(logger, "detect_scenes_by_diff", 
                         video_path=video_path, 
                         output_dir=output_dir,
                         diff_threshold=diff_threshold,
                         min_scene_length=min_scene_length)
        
        try:
            logger.info(f"Detectando cenas por diferença de quadros no vídeo: {video_path}")
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Não foi possível abrir o vídeo {video_path}")
                raise ValueError(f"Não foi possível abrir o vídeo {video_path}")
            
            prev_frame = None
            frame_count = 0
            scene_count = 0
            last_scene_frame = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if prev_frame is not None:
                    diff = cv2.absdiff(prev_frame, gray_frame)
                    diff_score = diff.sum() / (diff.shape[0] * diff.shape[1])
                    
                    if diff_score > diff_threshold and (frame_count - last_scene_frame) > min_scene_length:
                        scene_count += 1
                        last_scene_frame = frame_count
                        frame_path = os.path.join(output_dir, f"scene_{scene_count:03d}.jpg")
                        cv2.imwrite(frame_path, frame)
                        logger.info(f"Cena {scene_count} detectada e salva em {frame_path}")
                
                prev_frame = gray_frame
                frame_count += 1
            
            cap.release()
            logger.info(f"Detecção de cenas concluída. Total de {scene_count} cenas detectadas.")
            
            log_process_end(logger, "detect_scenes_by_diff")
            return output_dir
            
        except Exception as e:
            logger.error(f"Erro ao detectar cenas: {str(e)}", exc_info=True)
            raise
