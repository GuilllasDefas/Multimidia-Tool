"""
Ponto de entrada principal para a aplicação Multimídia Tools.
Este arquivo inicializa o ambiente e lança a interface gráfica.
"""

import sys
import os
import logging

# Configurar ambiente de execução
def setup_environment():
    """Configura o ambiente de execução."""
    # Determinar base_dir
    if getattr(sys, 'frozen', False):
        # Executando como arquivo compilado
        base_dir = os.path.dirname(sys.executable)
    else:
        # Executando em desenvolvimento
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Criar diretório de logs se não existir
    logs_dir = os.path.join(base_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    return base_dir


# Configurar ambiente antes de fazer qualquer importação dos módulos do projeto
base_dir = setup_environment()

# As importações devem ser feitas depois de configurar o ambiente
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainApplication
from utils.logging_utils import setup_logger


def main():
    """
    Função principal da aplicação.

    Configura o ambiente e inicia a interface gráfica principal.

    Returns:
        int: Código de saída (0 para sucesso, 1 para erro)
    """

    try:
        app = QApplication(sys.argv)
        main_window = MainApplication()
        main_window.show()
        sys.exit(app.exec_())

    except Exception as e:
        logging.error(
            f'Erro não tratado na aplicação: {str(e)}', exc_info=True
        )
        print(f'Ocorreu um erro: {str(e)}')
        return 1


if __name__ == '__main__':
    main()
