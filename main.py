"""
Ponto de entrada principal para a aplicação.
"""

import os
import sys
import logging
from ui.main_window import MainApplication
from utils.logging_utils import setup_logger


def setup_environment():
    """
    Configura o ambiente da aplicação.
    """
    logger = setup_logger("main")  # Certificar que o logger está configurado corretamente
    
    try:
        # Verificar existência de diretórios necessários
        base_dir = os.path.dirname(os.path.abspath(__file__))
        required_dirs = ['logs', 'models']
        
        for directory in required_dirs:
            dir_path = os.path.join(base_dir, directory)
            if not os.path.exists(dir_path):
                logger.info(f"Criando diretório: {dir_path}")
                os.makedirs(dir_path, exist_ok=True)
            elif not os.access(dir_path, os.W_OK):
                raise PermissionError(f"Sem permissão de escrita no diretório: {dir_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao configurar o ambiente: {str(e)}", exc_info=True)
        return False

def main():
    """Função principal da aplicação."""
    
    if not setup_environment():
        print("Falha ao configurar o ambiente da aplicação.")
        return 1
    
    try:
        app = MainApplication()
        app.mainloop()
        return 0
        
    except Exception as e:
        logging.error(f"Erro não tratado na aplicação: {str(e)}", exc_info=True)
        print(f"Ocorreu um erro: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
