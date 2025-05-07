"""
Utilitários de logging para a aplicação.
"""

import os
import logging
import datetime
from config.settings import LOG_DIR  # Certificar que o LOG_DIR está definido corretamente

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Configura e retorna um logger com o nome especificado.
    
    Args:
        name (str): Nome do logger.
        log_file (str, optional): Caminho para o arquivo de log. Se None, gera um nome baseado no timestamp.
        level (int, optional): Nível de logging. Padrão é logging.INFO.
        
    Returns:
        logging.Logger: Objeto logger configurado.
    """
    if log_file is None:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = f"{name}_{current_time}.log"
    
    log_path = os.path.join(LOG_DIR, log_file)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Verificar se o logger já tem handlers para evitar duplicação
    if not logger.handlers:
        # Criar o handler de arquivo
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        
        # Criar o handler de console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # Definir o formato
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                     datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Adicionar os handlers ao logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

def log_process_start(logger, process_name, **params):
    """
    Registra o início de um processo com seus parâmetros.
    
    Args:
        logger (logging.Logger): Logger a ser usado.
        process_name (str): Nome do processo.
        **params: Parâmetros do processo.
    """
    logger.info(f"Iniciando processo: {process_name}")
    if params:
        logger.info(f"Parâmetros: {params}")

def log_process_end(logger, process_name, duration=None):
    """
    Registra o fim de um processo.
    
    Args:
        logger (logging.Logger): Logger a ser usado.
        process_name (str): Nome do processo.
        duration (float, optional): Duração do processo em segundos.
    """
    if duration is not None:
        logger.info(f"Processo finalizado: {process_name}. Duração: {duration:.2f}s")
    else:
        logger.info(f"Processo finalizado: {process_name}")
