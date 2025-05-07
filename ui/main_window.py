"""
Interface principal da aplicação.
"""

import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
from PIL import Image, ImageTk
import sys

from ui.widgets import FileSelector, DirectorySelector, StatusBar, ProcessingTab, ModernButton
from ui.theme import setup_modern_theme, COLORS
from core.video_processor import VideoProcessor
from core.frame_extractor import FrameExtractor
from core.image_enhancer import ImageEnhancer
from core.transcriber import Transcriber
from config.settings import VIDEO_SETTINGS, FRAME_EXTRACTION, UPSCALE_SETTINGS, TRANSCRIPTION_SETTINGS, SUPPORTED_EXTENSIONS
from utils.logging_utils import setup_logger

logger = setup_logger("main_ui")

class MainApplication(tk.Tk):
    """Classe principal da aplicação."""
    
    def __init__(self):
        """Inicializa a aplicação principal."""
        super().__init__()
        
        self.title("Multimídia Tools Pro")
        self.geometry("900x750")
        self.minsize(900, 650)
        
        # Configurar o ícone da aplicação se disponível
        try:
            # Adaptar para caminho de ícone adequado
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "app_icon.png")
            if os.path.exists(icon_path):
                self.iconphoto(True, tk.PhotoImage(file=icon_path))
        except Exception as e:
            logger.warning(f"Não foi possível carregar o ícone: {e}")
        
        # Configurar tema moderno
        self.style = ttk.Style(self)
        setup_modern_theme(self)
        
        # Configurar cores de fundo
        self.configure(background=COLORS['bg_main'])
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Cria os widgets da janela principal."""
        # Cabeçalho com título
        header_frame = tk.Frame(self, bg=COLORS['primary'], height=60)
        header_frame.pack(fill="x", side="top")
        
        title_label = tk.Label(
            header_frame, 
            text="MULTIMÍDIA TOOLS PRO", 
            font=("Segoe UI", 16, "bold"),
            bg=COLORS['primary'], 
            fg="white"
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        # Criar notebook (abas) com estilo moderno
        self.notebook = ttk.Notebook(self, style='Modern.TNotebook')
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Criar as abas
        self.video_tab = VideoEditorTab(self.notebook)
        self.frames_tab = FrameExtractorTab(self.notebook)
        self.upscale_tab = ImageUpscalerTab(self.notebook)
        self.transcribe_tab = TranscriptionTab(self.notebook)
        
        # Adicionar as abas ao notebook
        self.notebook.add(self.video_tab, text="Editor de Vídeo")
        self.notebook.add(self.frames_tab, text="Extração de Frames")
        self.notebook.add(self.upscale_tab, text="Upscale de Imagem")
        self.notebook.add(self.transcribe_tab, text="Transcrição")
        
        # Barra de status
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill="x", side="bottom", padx=10, pady=5)
        
        # Configurar eventos
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def _on_close(self):
        """Manipulador para o evento de fechamento da janela."""
        if messagebox.askokcancel("Sair", "Deseja realmente sair da aplicação?"):
            self.destroy()
            
class VideoEditorTab(ProcessingTab):
    """Aba para edição de vídeos."""
    
    def __init__(self, parent):
        """Inicializa a aba de edição de vídeos."""
        super().__init__(parent, title="Editor de Vídeo")
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Cria os widgets específicos para a aba de edição de vídeos."""
        # Seletor de arquivo
        self.file_selector = FileSelector(
            self.controls_frame, 
            file_types=[("Arquivos de vídeo", "*.mp4 *.mov *.avi *.mkv")],
            title="Selecione o arquivo de vídeo"
        )
        self.file_selector.pack(fill="x", padx=10, pady=10)
        
        # Opções de remoção de silêncio
        options_inner_frame = ttk.Frame(self.options_frame, style="Card.TFrame")
        options_inner_frame.pack(fill="x", padx=10, pady=10, expand=True)
        
        # Slider para limiar de silêncio
        ttk.Label(options_inner_frame, text="Limiar de silêncio (dB):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.silence_threshold = tk.IntVar(value=VIDEO_SETTINGS['silence_threshold'])
        self.threshold_scale = ttk.Scale(
            options_inner_frame, 
            from_=-100, 
            to=0, 
            variable=self.silence_threshold,
            orient="horizontal",
            length=200
        )
        self.threshold_scale.grid(row=0, column=1, padx=10, pady=10, sticky="we")
        self.silence_threshold_label = ttk.Label(options_inner_frame, text=str(self.silence_threshold.get()))
        self.silence_threshold_label.grid(row=0, column=2, padx=5, pady=10)
        self.threshold_scale.configure(command=lambda v: self.silence_threshold_label.configure(text=str(int(float(v)))))
        
        # Slider para duração mínima
        ttk.Label(options_inner_frame, text="Duração mínima silêncio (ms):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.min_silence_len = tk.IntVar(value=VIDEO_SETTINGS['min_silence_len'])
        self.min_silence_scale = ttk.Scale(
            options_inner_frame, 
            from_=100, 
            to=10000, 
            variable=self.min_silence_len,
            orient="horizontal",
            length=200
        )
        self.min_silence_scale.grid(row=1, column=1, padx=10, pady=10, sticky="we")
        self.min_silence_label = ttk.Label(options_inner_frame, text=str(self.min_silence_len.get()))
        self.min_silence_label.grid(row=1, column=2, padx=5, pady=10)
        self.min_silence_scale.configure(command=lambda v: self.min_silence_label.configure(text=str(int(float(v)))))
        
        # Slider para padding
        ttk.Label(options_inner_frame, text="Padding (ms):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.padding = tk.IntVar(value=VIDEO_SETTINGS['silence_padding'])
        self.padding_scale = ttk.Scale(
            options_inner_frame, 
            from_=-5000, 
            to=5000, 
            variable=self.padding,
            orient="horizontal",
            length=200
        )
        self.padding_scale.grid(row=2, column=1, padx=10, pady=10, sticky="we")
        self.padding_label = ttk.Label(options_inner_frame, text=str(self.padding.get()))
        self.padding_label.grid(row=2, column=2, padx=5, pady=10)
        self.padding_scale.configure(command=lambda v: self.padding_label.configure(text=str(int(float(v)))))
        
        options_inner_frame.columnconfigure(1, weight=1)
        
        # Botão para processar
        self.process_button = ModernButton(
            self.controls_frame, 
            text="Remover Silêncios", 
            command=self._process_video,
            width=20
        )
        self.process_button.pack(pady=15)
        
    def _process_video(self):
        """Inicia o processamento do vídeo."""
        video_path = self.file_selector.get_path()
        
        if not video_path:
            messagebox.showerror("Erro", "Selecione um arquivo de vídeo.")
            return
            
        if not os.path.exists(video_path):
            messagebox.showerror("Erro", f"Arquivo não encontrado: {video_path}")
            return
        
        # Desabilitar botão durante o processamento
        self.process_button.configure(state="disabled")
        self.set_status("Processando vídeo...")
        self.start_progress()
        
        # Iniciar o processamento em uma thread separada
        threading.Thread(
            target=self._run_video_processing, 
            args=(video_path,),
            daemon=True
        ).start()
        
    def _run_video_processing(self, video_path):
        """
        Executa o processamento de vídeo em uma thread separada.
        
        Args:
            video_path (str): Caminho do vídeo a ser processado.
        """
        try:
            # Criar processador de vídeo com as opções selecionadas
            processor = VideoProcessor(
                silence_thresh=self.silence_threshold.get(),
                min_silence_len=self.min_silence_len.get(),
                padding=self.padding.get()
            )
            
            # Processar o vídeo
            output_path = processor.remove_silence(video_path)
            
            # Atualizar a UI na thread principal
            self.after(0, self._processing_finished, output_path)
            
        except Exception as e:
            # Tratar erros
            logger.error(f"Erro ao processar vídeo: {str(e)}", exc_info=True)
            self.after(0, self._processing_error, str(e))
    
    def _processing_finished(self, output_path):
        """
        Callback para quando o processamento é concluído com sucesso.
        
        Args:
            output_path (str): Caminho do vídeo processado.
        """
        self.process_button.configure(state="normal")
        self.stop_progress()
        self.set_status("Processamento concluído!")
        messagebox.showinfo("Concluído", f"Vídeo processado com sucesso!\nSalvo em:\n{output_path}")
    
    def _processing_error(self, error_message):
        """
        Callback para quando ocorre um erro durante o processamento.
        
        Args:
            error_message (str): Mensagem de erro.
        """
        self.process_button.configure(state="normal")
        self.stop_progress()
        self.set_status(f"Erro: {error_message}")
        messagebox.showerror("Erro", f"Ocorreu um erro durante o processamento:\n{error_message}")

class FrameExtractorTab(ProcessingTab):
    """Aba para extração de frames de vídeos."""
    
    def __init__(self, parent):
        """Inicializa a aba de extração de frames."""
        super().__init__(parent, title="Extração de Frames")
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Cria os widgets específicos para a aba de extração de frames."""
        # Seletor de arquivo
        self.file_selector = FileSelector(
            self.controls_frame, 
            file_types=[("Arquivos de vídeo", "*.mp4 *.mov *.avi *.mkv")],
            title="Selecione o arquivo de vídeo"
        )
        self.file_selector.pack(fill="x", padx=5, pady=5)
        
        # Opções de extração
        ttk.Label(self.options_frame, text="Método de extração:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.extraction_method = tk.StringVar(value="cenas")
        ttk.Radiobutton(self.options_frame, text="Detecção de cenas", variable=self.extraction_method, value="cenas").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(self.options_frame, text="Frames regulares", variable=self.extraction_method, value="regulares").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(self.options_frame, text="Diferença entre quadros", variable=self.extraction_method, value="diferenca").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Frame para opções adicionais
        self.adv_options_frame = ttk.Frame(self.options_frame)
        self.adv_options_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        
        # Opções para detecção de cenas
        ttk.Label(self.adv_options_frame, text="Threshold:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.threshold = tk.DoubleVar(value=FRAME_EXTRACTION['threshold'])
        self.threshold_spin = ttk.Spinbox(self.adv_options_frame, from_=0.1, to=100.0, increment=0.1, textvariable=self.threshold, width=5)
        self.threshold_spin.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(self.adv_options_frame, text="Intervalo de frames:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.interval = tk.IntVar(value=FRAME_EXTRACTION['default_interval'])
        self.interval_spin = ttk.Spinbox(self.adv_options_frame, from_=1, to=1000, increment=10, textvariable=self.interval, width=5)
        self.interval_spin.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Detector options
        self.use_threshold_detector = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.adv_options_frame, text="Usar ThresholdDetector", variable=self.use_threshold_detector).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Botão para processar
        self.process_button = ttk.Button(self.controls_frame, text="Extrair Frames", command=self._extract_frames)
        self.process_button.pack(pady=10)
        
    def _extract_frames(self):
        """Inicia a extração de frames."""
        video_path = self.file_selector.get_path()
        
        if not video_path:
            messagebox.showerror("Erro", "Selecione um arquivo de vídeo.")
            return
            
        if not os.path.exists(video_path):
            messagebox.showerror("Erro", f"Arquivo não encontrado: {video_path}")
            return
        
        # Desabilitar botão durante o processamento
        self.process_button.configure(state="disabled")
        self.set_status("Extraindo frames...")
        self.start_progress()
        
        # Iniciar o processamento em uma thread separada
        threading.Thread(
            target=self._run_frame_extraction,
            args=(video_path,),
            daemon=True
        ).start()
        
    def _run_frame_extraction(self, video_path):
        """
        Executa a extração de frames em uma thread separada.
        
        Args:
            video_path (str): Caminho do vídeo para extrair frames.
        """
        try:
            # Criar extrator de frames com as opções selecionadas
            extractor = FrameExtractor(
                threshold=self.threshold.get(),
                max_frames=FRAME_EXTRACTION['max_frames']
            )
            
            # Escolher o método de extração
            method = self.extraction_method.get()
            output_dir = None
            
            if method == "cenas":
                output_dir = extractor.extract_keyframes(
                    video_path, 
                    usar_threshold_detector=self.use_threshold_detector.get()
                )
            elif method == "regulares":
                output_dir = extractor.extract_regular_frames(
                    video_path, 
                    intervalo=self.interval.get()
                )
            elif method == "diferenca":
                output_dir = extractor.detect_scenes_by_diff(
                    video_path, 
                    diff_threshold=int(self.threshold.get()),
                    min_scene_length=FRAME_EXTRACTION['min_scene_length']
                )
            
            # Atualizar a UI na thread principal
            self.after(0, self._extraction_finished, output_dir)
            
        except Exception as e:
            # Tratar erros
            logger.error(f"Erro ao extrair frames: {str(e)}", exc_info=True)
            self.after(0, self._processing_error, str(e))
    
    def _extraction_finished(self, output_dir):
        """
        Callback para quando a extração é concluída com sucesso.
        
        Args:
            output_dir (str): Diretório onde os frames foram salvos.
        """
        self.process_button.configure(state="normal")
        self.stop_progress()
        self.set_status("Extração concluída!")
        messagebox.showinfo("Concluído", f"Frames extraídos com sucesso!\nSalvos em:\n{output_dir}")
    
    def _processing_error(self, error_message):
        """
        Callback para quando ocorre um erro durante a extração.
        
        Args:
            error_message (str): Mensagem de erro.
        """
        self.process_button.configure(state="normal")
        self.stop_progress()
        self.set_status(f"Erro: {error_message}")
        messagebox.showerror("Erro", f"Ocorreu um erro durante a extração:\n{error_message}")

class ImageUpscalerTab(ProcessingTab):
    """Aba para upscaling de imagens."""
    
    def __init__(self, parent):
        """Inicializa a aba de upscaling de imagens."""
        super().__init__(parent, title="Upscaling de Imagens")
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets específicos para a aba de upscaling de imagens."""
        # Modos de operação
        self.operation_mode = tk.StringVar(value="file")
        
        ttk.Radiobutton(
            self.controls_frame, 
            text="Processar uma imagem", 
            variable=self.operation_mode, 
            value="file",
            command=self._update_selector_mode
        ).pack(padx=5, pady=5, anchor="w")
        
        ttk.Radiobutton(
            self.controls_frame, 
            text="Processar pasta completa", 
            variable=self.operation_mode, 
            value="dir",
            command=self._update_selector_mode
        ).pack(padx=5, pady=5, anchor="w")
        
        # Container para os seletores
        self.selector_container = ttk.Frame(self.controls_frame)
        self.selector_container.pack(fill="x", padx=5, pady=5)
        
        # Seletor de arquivo
        self.file_selector = FileSelector(
            self.selector_container, 
            file_types=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.tiff")],
            title="Selecione a imagem"
        )
        
        # Seletor de diretório
        self.dir_selector = DirectorySelector(
            self.selector_container,
            title="Selecione a pasta com imagens"
        )
        
        # Opções de upscaling
        ttk.Label(self.options_frame, text="Fator de escala:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.scale_factor = tk.IntVar(value=UPSCALE_SETTINGS['scale'])
        self.scale_spin = ttk.Spinbox(self.options_frame, from_=2, to=8, increment=1, textvariable=self.scale_factor, width=5)
        self.scale_spin.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Botão para processar
        self.process_button = ttk.Button(self.controls_frame, text="Aumentar Resolução", command=self._process_images)
        self.process_button.pack(pady=10)
        
        # Inicializar o seletor apropriado
        self._update_selector_mode()
    
    def _update_selector_mode(self):
        """Atualiza o seletor de acordo com o modo selecionado."""
        mode = self.operation_mode.get()
        
        # Limpar o container
        for child in self.selector_container.winfo_children():
            child.pack_forget()
        
        # Mostrar o seletor apropriado
        if mode == "file":
            self.file_selector.pack(fill="x")
        else:
            self.dir_selector.pack(fill="x")
    
    def _process_images(self):
        """Inicia o processamento de imagens."""
        mode = self.operation_mode.get()
        path = None
        
        if mode == "file":
            path = self.file_selector.get_path()
            if not path:
                messagebox.showerror("Erro", "Selecione uma imagem.")
                return
        else:
            path = self.dir_selector.get_path()
            if not path:
                messagebox.showerror("Erro", "Selecione uma pasta.")
                return
        
        if not os.path.exists(path):
            messagebox.showerror("Erro", f"Caminho não encontrado: {path}")
            return
        
        # Desabilitar botão durante o processamento
        self.process_button.configure(state="disabled")
        self.set_status("Processando imagens...")
        self.start_progress()
        
        # Iniciar o processamento em uma thread separada
        threading.Thread(
            target=self._run_image_processing,
            args=(path, mode),
            daemon=True
        ).start()
    
    def _run_image_processing(self, path, mode):
        """
        Executa o processamento de imagens em uma thread separada.
        
        Args:
            path (str): Caminho da imagem ou diretório.
            mode (str): Modo de operação ('file' ou 'dir').
        """
        try:
            # Criar enhancer com as opções selecionadas
            enhancer = ImageEnhancer(
                scale=self.scale_factor.get()
            )
            
            # Processar de acordo com o modo
            if mode == "file":
                output_path = enhancer.enhance_image(path)
                self.after(0, self._processing_finished_file, output_path)
            else:
                output_dir = enhancer.process_directory(path)
                self.after(0, self._processing_finished_dir, output_dir)
            
        except Exception as e:
            # Tratar erros
            logger.error(f"Erro ao processar imagens: {str(e)}", exc_info=True)
            self.after(0, self._processing_error, str(e))
    
    def _processing_finished_file(self, output_path):
        """
        Callback para quando o processamento de um arquivo é concluído.
        
        Args:
            output_path (str): Caminho da imagem processada.
        """
        self.process_button.configure(state="normal")
        self.stop_progress()
        self.set_status("Processamento concluído!")
        messagebox.showinfo("Concluído", f"Imagem processada com sucesso!\nSalva em:\n{output_path}")
    
    def _processing_finished_dir(self, output_dir):
        """
        Callback para quando o processamento de um diretório é concluído.
        
        Args:
            output_dir (str): Diretório onde as imagens processadas foram salvas.
        """
        self.process_button.configure(state="normal")
        self.stop_progress()
        self.set_status("Processamento concluído!")
        messagebox.showinfo("Concluído", f"Todas as imagens foram processadas!\nSalvas em:\n{output_dir}")
    
    def _processing_error(self, error_message):
        """
        Callback para quando ocorre um erro durante o processamento.
        
        Args:
            error_message (str): Mensagem de erro.
        """
        self.process_button.configure(state="normal")
        self.stop_progress()
        self.set_status(f"Erro: {error_message}")
        messagebox.showerror("Erro", f"Ocorreu um erro durante o processamento:\n{error_message}")

class TranscriptionTab(ProcessingTab):
    """Aba para transcrição de áudio/vídeo."""
    
    def __init__(self, parent):
        """Inicializa a aba de transcrição."""
        super().__init__(parent, title="Transcrição")
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets específicos para a aba de transcrição."""
        # Seletor de arquivo
        self.file_selector = FileSelector(
            self.controls_frame, 
            file_types=[
                ("Arquivos de mídia", "*.mp4 *.mov *.mp3 *.wav *.m4a *.ogg"),
                ("Arquivos de vídeo", "*.mp4 *.mov *.avi *.mkv *.wmv *.flv"),
                ("Arquivos de áudio", "*.mp3 *.wav *.m4a *.ogg *.flac *.aac"),
            ],
            title="Selecione o arquivo de áudio ou vídeo"
        )
        self.file_selector.pack(fill="x", padx=5, pady=5)
        
        # Opções de transcrição
        ttk.Label(self.options_frame, text="Modelo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.model = tk.StringVar(value=TRANSCRIPTION_SETTINGS['model'])
        model_combo = ttk.Combobox(self.options_frame, textvariable=self.model, width=10)
        model_combo['values'] = ('tiny', 'base', 'small', 'medium', 'large')
        model_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(self.options_frame, text="Idioma:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.language = tk.StringVar(value=TRANSCRIPTION_SETTINGS['language'])
        language_combo = ttk.Combobox(self.options_frame, textvariable=self.language, width=10)
        language_combo['values'] = ('pt', 'en', 'es', 'fr', 'de', 'it', 'auto')
        language_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Botão para processar
        self.process_button = ttk.Button(self.controls_frame, text="Transcrever", command=self._transcribe_file)
        self.process_button.pack(pady=10)
        
        # Área para mostrar a transcrição
        ttk.Label(self, text="Transcrição:").pack(anchor="w", padx=5, pady=(10, 0))
        
        self.transcription_frame = ttk.Frame(self)
        self.transcription_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.transcription_text = tk.Text(self.transcription_frame, wrap="word", height=10)
        self.transcription_text.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(self.transcription_frame, command=self.transcription_text.yview)
        scrollbar.pack(fill="y", side="right")
        self.transcription_text.config(yscrollcommand=scrollbar.set)
    
    def _transcribe_file(self):
        """Inicia a transcrição do arquivo."""
        file_path = self.file_selector.get_path()
        
        if not file_path:
            messagebox.showerror("Erro", "Selecione um arquivo de áudio ou vídeo.")
            return
            
        if not os.path.exists(file_path):
            messagebox.showerror("Erro", f"Arquivo não encontrado: {file_path}")
            return
        
        # Desabilitar botão durante o processamento
        self.process_button.configure(state="disabled")
        self.set_status("Transcrevendo arquivo...")
        self.start_progress()
        self.transcription_text.delete(1.0, tk.END)
        
        # Iniciar o processamento em uma thread separada
        threading.Thread(
            target=self._run_transcription,
            args=(file_path,),
            daemon=True
        ).start()
    
    def _run_transcription(self, file_path):
        """
        Executa a transcrição em uma thread separada.
        
        Args:
            file_path (str): Caminho do arquivo a ser transcrito.
        """
        try:
            # Criar transcritor com as opções selecionadas
            transcriber = Transcriber(
                model_name=self.model.get(),
                language=self.language.get()
            )
            
            # Transcrever o arquivo
            output_path, srt_path, text = transcriber.transcribe(file_path)
            
            # Atualizar a UI na thread principal
            self.after(0, self._transcription_finished, output_path, srt_path, text)
            
        except Exception as e:
            # Tratar erros
            logger.error(f"Erro ao transcrever arquivo: {str(e)}", exc_info=True)
            self.after(0, self._processing_error, str(e))
    
    def _transcription_finished(self, output_path, srt_path, text):
        """
        Callback para quando a transcrição é concluída com sucesso.
        
        Args:
            output_path (str): Caminho do arquivo de texto da transcrição.
            srt_path (str): Caminho do arquivo de legendas SRT.
            text (str): Texto transcrito.
        """
        self.process_button.configure(state="normal")
        self.stop_progress()
        self.set_status("Transcrição concluída!")
        
        # Mostrar o texto transcrito
        self.transcription_text.delete(1.0, tk.END)
        self.transcription_text.insert(1.0, text)
        
        messagebox.showinfo("Concluído", f"Transcrição concluída!\nTexto salvo em: {output_path}\nLegendas salvas em: {srt_path}")
    
    def _processing_error(self, error_message):
        """
        Callback para quando ocorre um erro durante a transcrição.
        
        Args:
            error_message (str): Mensagem de erro.
        """
        self.process_button.configure(state="normal")
        self.stop_progress()
        self.set_status(f"Erro: {error_message}")
        messagebox.showerror("Erro", f"Ocorreu um erro durante a transcrição:\n{error_message}")
