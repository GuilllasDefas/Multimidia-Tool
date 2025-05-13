"""
Funções utilitárias para manipulação de arquivos.
"""

import os
import tempfile
from config.settings import (
    SUPPORTED_EXTENSIONS,
)  # Certificar que SUPPORTED_EXTENSIONS está definido corretamente


def is_supported_file(file_path, file_type=None):
    """
    Verifica se um arquivo tem uma extensão suportada.

    Args:
        file_path (str): Caminho para o arquivo.
        file_type (str, optional): Tipo de arquivo ('video', 'audio', 'image').
                                  Se None, verifica todos os tipos.

    Returns:
        bool: True se o arquivo for suportado, False caso contrário.
    """
    _, ext = os.path.splitext(file_path.lower())

    if file_type:
        return ext in SUPPORTED_EXTENSIONS.get(file_type, [])

    # Verificar em todos os tipos
    for extensions in SUPPORTED_EXTENSIONS.values():
        if ext in extensions:
            return True

    return False


def get_output_path(input_path, suffix, extension=None):
    """
    Gera um caminho de saída baseado no caminho de entrada.

    Args:
        input_path (str): Caminho do arquivo de entrada.
        suffix (str): Sufixo a ser adicionado ao nome do arquivo.
        extension (str, optional): Se fornecido, substitui a extensão do arquivo.

    Returns:
        str: Caminho de saída gerado.
    """
    directory = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)

    if extension:
        ext = extension

    output_filename = f'{name}{suffix}{ext}'
    return os.path.join(directory, output_filename)


def create_temp_file(suffix=None):
    """
    Cria um arquivo temporário.

    Args:
        suffix (str, optional): Sufixo para o arquivo temporário.

    Returns:
        str: Caminho para o arquivo temporário.
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    temp_path = temp_file.name
    temp_file.close()
    return temp_path


def ensure_dir_exists(directory):
    """
    Garante que um diretório existe, criando-o se necessário.

    Args:
        directory (str): Caminho do diretório.

    Returns:
        str: Caminho do diretório.
    """
    os.makedirs(directory, exist_ok=True)
    return directory
