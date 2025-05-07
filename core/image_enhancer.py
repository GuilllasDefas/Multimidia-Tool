"""
Módulo para melhoramento e upscaling de imagens.
"""

import os
import numpy as np
import torch
from PIL import Image
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from tqdm import tqdm

from config.settings import UPSCALE_SETTINGS
from utils.logging_utils import setup_logger, log_process_start, log_process_end
from utils.file_utils import ensure_dir_exists, is_supported_file

logger = setup_logger("image_enhancer")

class ImageEnhancer:
    """Classe para aprimoramento e upscale de imagens."""
    
    def __init__(self, model_path="models", scale=None):
        """
        Inicializa o aprimorador de imagens com o modelo especificado.
        
        Args:
            model_path (str, optional): Caminho para o arquivo do modelo.
            scale (int, optional): Fator de escala para upscaling.
        """
        self.model_path = model_path or UPSCALE_SETTINGS['model_name']
        self.scale = scale or UPSCALE_SETTINGS['scale']
        self.upsampler = None
        self.device = None
        
    def load_model(self):
        """
        Carrega o modelo Real-ESRGAN para super-resolução.
        
        Returns:
            tuple: (RealESRGANer, device) - O upsampler e o dispositivo usado.
        """
        if self.upsampler is not None:
            return self.upsampler, self.device
            
        log_process_start(logger, "load_model", model_path=self.model_path)
        
        try:
            # Determinar o dispositivo a ser usado
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"Usando dispositivo: {self.device}")
            
            # Localizar o modelo
            if self.model_path.lower() == "models":
                # Substituir por nome de arquivo do modelo
                self.model_path = "RealESRGAN_x4plus.pth"

            models_subdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
            model_filename = os.path.basename(self.model_path)
            model_full_path = os.path.join(models_subdir, model_filename)

            if not os.path.exists(models_subdir):
                raise FileNotFoundError(f"Diretório 'models' não encontrado: {models_subdir}")

            if os.path.isdir(model_full_path):
                raise FileNotFoundError(
                    f"Foi fornecido um diretório em vez de um arquivo de modelo: {model_full_path}"
                )

            if not os.path.exists(model_full_path):
                raise FileNotFoundError(f"Modelo não encontrado: {model_full_path}")
            if not os.access(model_full_path, os.R_OK):
                raise PermissionError(f"Sem permissão de leitura no arquivo do modelo: {model_full_path}")
            self.model_path = model_full_path
            
            # Carregar os pesos do modelo
            logger.info(f"Carregando pesos do modelo de {self.model_path}")
            pesos = torch.load(self.model_path, map_location=self.device)['params_ema']
            
            # Definir a arquitetura do modelo
            modelo = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
            modelo.load_state_dict(pesos, strict=True)
            modelo.to(self.device)
            
            # Configurar o upsampler
            self.upsampler = RealESRGANer(
                scale=2,
                model_path=self.model_path,
                model=modelo,
                tile=0,
                pre_pad=0,
                half=(self.device.type == "cuda"),  # Usar precisão reduzida apenas na GPU
                device=self.device,
            )
            
            log_process_end(logger, "load_model")
            return self.upsampler, self.device
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {str(e)}", exc_info=True)
            raise
    
    def enhance_image(self, input_path, output_path=None):
        """
        Aumenta a resolução de uma imagem usando o modelo carregado.
        
        Args:
            input_path (str): Caminho da imagem de entrada.
            output_path (str, optional): Caminho para salvar a imagem processada.
            
        Returns:
            str: Caminho da imagem processada.
        """
        if output_path is None:
            directory = os.path.dirname(input_path)
            filename = os.path.basename(input_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(directory, f"{name}_upscaled{ext}")
        
        log_process_start(logger, "enhance_image", 
                         input_path=input_path, 
                         output_path=output_path,
                         scale=self.scale)
        
        try:
            # Carregar modelo se ainda não foi carregado
            upsampler, _ = self.load_model()
            
            # Carregar e processar a imagem
            logger.info(f"Convertendo imagem para RGB: {input_path}...")
            imagem = Image.open(input_path).convert("RGB")
            
            logger.info(f"Convertendo imagem para Array: {input_path}...")
            imagem_array = np.array(imagem)
            
            logger.info(f"Aumentando resolução da imagem: {input_path}...")
            imagem_saida, _ = upsampler.enhance(imagem_array, outscale=self.scale)
            
            logger.info(f"Convertendo de volta para imagem: {input_path}...")
            imagem_final = Image.fromarray(imagem_saida)
            
            logger.info(f"Salvando imagem: {output_path}...")
            imagem_final.save(output_path)
            
            log_process_end(logger, "enhance_image")
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao aumentar resolução da imagem: {str(e)}", exc_info=True)
            raise
    
    def process_directory(self, input_dir, output_dir=None):
        """
        Processa todas as imagens em um diretório para aumentar a resolução.
        
        Args:
            input_dir (str): Diretório com as imagens de entrada.
            output_dir (str, optional): Diretório onde as imagens processadas serão salvas.
            
        Returns:
            str: Diretório onde as imagens foram salvas.
        """
        if output_dir is None:
            output_dir = os.path.join(input_dir, "upscale_output")
        
        output_dir = ensure_dir_exists(output_dir)
        
        log_process_start(logger, "process_directory", 
                         input_dir=input_dir, 
                         output_dir=output_dir)
        
        try:
            # Listar todas as imagens na pasta
            files = os.listdir(input_dir)
            imagens = [f for f in files if is_supported_file(os.path.join(input_dir, f), 'image')]
            
            if not imagens:
                logger.warning("Nenhuma imagem encontrada na pasta selecionada.")
                return output_dir
            
            logger.info(f"Encontradas {len(imagens)} imagens para processamento.")
            
            # Carregar modelo
            self.load_model()
            
            # Processar cada imagem com feedback de progresso
            for imagem in tqdm(imagens, desc="Processando imagens"):
                input_path = os.path.join(input_dir, imagem)
                nome_arquivo, extensao = os.path.splitext(imagem)
                output_path = os.path.join(output_dir, f"{nome_arquivo}_upscaled{extensao}")
                
                try:
                    self.enhance_image(input_path, output_path)
                except Exception as e:
                    logger.error(f"Erro ao processar {imagem}: {str(e)}")
            
            log_process_end(logger, "process_directory")
            return output_dir
            
        except Exception as e:
            logger.error(f"Erro ao processar diretório: {str(e)}", exc_info=True)
            raise
