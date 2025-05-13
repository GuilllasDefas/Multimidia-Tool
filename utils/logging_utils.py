"""
Utilitários de logging para a aplicação.
"""

import os
import sys
import logging
import datetime


def setup_logger(logger_name):
    """Configura e retorna um logger com nome personalizado."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Determinar se estamos em um ambiente congelado (exe) ou não
    if getattr(sys, 'frozen', False):
        # Se estamos rodando como um executável compilado
        base_dir = os.path.dirname(sys.executable)
    else:
        # Se estamos rodando em desenvolvimento
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Criar diretório de logs se não existir
    log_dir = os.path.join(base_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Criar nome do arquivo de log com timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_path = os.path.join(log_dir, f'{logger_name}_{timestamp}.log')

    # Adicionar file handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)

    # Configurar formatação do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)

    # Adicionar console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
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
    logger.info(f'Iniciando processo: {process_name}')
    if params:
        logger.info(f'Parâmetros: {params}')


def log_process_end(logger, process_name, duration=None):
    """
    Registra o fim de um processo.

    Args:
        logger (logging.Logger): Logger a ser usado.
        process_name (str): Nome do processo.
        duration (float, optional): Duração do processo em segundos.
    """
    if duration is not None:
        logger.info(
            f'Processo finalizado: {process_name}. Duração: {duration:.2f}s'
        )
    else:
        logger.info(f'Processo finalizado: {process_name}')
