# Multimídia Tools

Uma aplicação para processamento e manipulação de arquivos multimídia com diversas funcionalidades:

- **Editor de Vídeo**: Remoção automática de silêncio em vídeos
- **Extrator de Frames**: Extração de frames-chave de vídeos
- **Upscaling de Imagens**: Aumento de resolução de imagens usando IA
- **Transcrição**: Conversão de áudio/vídeo para texto

## Estrutura do Projeto

```
Multimidia Tool/
├── main.py                   # Ponto de entrada principal
├── README.md                 # Este arquivo
├── setup.py                  # Script para criar executável com cx_Freeze
├── config/                   # Configurações centralizadas
│   ├── __init__.py
│   └── settings.py           # Parâmetros configuráveis
├── core/                     # Lógica de negócio principal
│   ├── __init__.py
│   ├── video_processor.py    # Processamento de vídeos
│   ├── frame_extractor.py    # Extração de frames-chave
│   ├── image_enhancer.py     # Upscaling de imagens
│   └── transcriber.py        # Transcrição áudio/vídeo
├── ui/                       # Interface do usuário
│   ├── __init__.py
│   ├── main_window.py        # Interface principal
│   └── widgets.py            # Componentes reutilizáveis
├── utils/                    # Funções utilitárias
│   ├── __init__.py
│   ├── file_utils.py         # Manipulação de arquivos
│   └── logging_utils.py      # Logging centralizado
├── logs/                     # Logs da aplicação (criado automaticamente)
└── models/                   # Modelos de IA (adicionar manualmente)
    └── RealESRGAN_x4plus.pth # Modelo para upscaling (baixar separadamente)
```

## Requisitos

- Python 3.10 ou superior
- As dependências listadas em `requirements.txt`

## Instalação

1. Clone ou baixe este repositório
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Baixe o modelo RealESRGAN_x4plus.pth e coloque-o na pasta `models/`
   (Disponível em: https://github.com/xinntao/Real-ESRGAN/releases)

## Uso

Execute o arquivo principal para iniciar a aplicação:
```
python main.py
```

A interface gráfica oferece acesso a todas as funcionalidades em abas separadas.

## Criando um Executável

Para criar um executável standalone:

1. Instale o cx_Freeze:
   ```
   pip install cx_Freeze
   ```

2. Execute o script setup.py:
   ```
   python setup.py build
   ```

3. O executável será criado na pasta `build/exe.{plataforma}/MultimidiaToolsPro.exe`