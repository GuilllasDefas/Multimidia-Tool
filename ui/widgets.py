"""
Componentes de interface do usuário reutilizáveis.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.messagebox import showinfo, showerror
import os
from ui.theme import COLORS


class ModernButton(tk.Button):
    """Botão com design moderno."""

    def __init__(self, parent, **kwargs):
        """
        Inicializa um botão moderno.

        Args:
            parent: Widget pai.
            **kwargs: Argumentos para o botão.
        """
        bg = kwargs.pop('bg', COLORS['primary'])
        fg = kwargs.pop('fg', 'white')
        activebackground = kwargs.pop(
            'activebackground', COLORS['primary_dark']
        )
        activeforeground = kwargs.pop('activeforeground', 'white')
        relief = kwargs.pop('relief', 'flat')
        borderwidth = kwargs.pop('borderwidth', 0)
        padx = kwargs.pop('padx', 20)
        pady = kwargs.pop('pady', 8)
        font = kwargs.pop('font', ('Segoe UI', 10))

        super().__init__(
            parent,
            bg=bg,
            fg=fg,
            activebackground=activebackground,
            activeforeground=activeforeground,
            relief=relief,
            borderwidth=borderwidth,
            padx=padx,
            pady=pady,
            font=font,
            cursor='hand2',
            **kwargs
        )

        # Efeitos de hover
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _on_enter(self, event):
        """Efeito ao passar o mouse."""
        self.config(bg=COLORS['primary_light'])

    def _on_leave(self, event):
        """Efeito ao retirar o mouse."""
        self.config(bg=COLORS['primary'])


class FileSelector(ttk.Frame):
    """Widget para seleção de arquivos."""

    def __init__(
        self, parent, file_types=None, title='Selecione um arquivo', **kwargs
    ):
        """
        Inicializa o seletor de arquivos.

        Args:
            parent: Widget pai.
            file_types (list, optional): Lista de tipos de arquivo.
            title (str, optional): Título da janela de seleção.
            **kwargs: Argumentos adicionais para o Frame.
        """
        super().__init__(parent, style='Card.TFrame', padding=10, **kwargs)

        self.file_types = file_types or [('Todos os arquivos', '*.*')]
        self.title = title
        self.selected_path = tk.StringVar()

        self._create_widgets()

    def _create_widgets(self):
        """Cria os widgets do seletor de arquivos."""
        # Label descritiva
        ttk.Label(self, text=self.title, style='Bold.TLabel').pack(
            anchor='w', pady=(0, 5)
        )

        # Frame para o campo e botão
        input_frame = ttk.Frame(self)
        input_frame.pack(fill='x', expand=True)

        # Campo de texto com borda arredondada
        self.path_entry = ttk.Entry(
            input_frame,
            textvariable=self.selected_path,
            width=50,
            style='Modern.TEntry',
        )
        self.path_entry.grid(row=0, column=0, padx=(0, 5), pady=5, sticky='we')

        # Botão para selecionar arquivo
        self.browse_button = ModernButton(
            input_frame,
            text='Procurar...',
            command=self._browse_file,
            width=12,
        )
        self.browse_button.grid(row=0, column=1, padx=5, pady=5)

        # Configurar o grid para expansão
        input_frame.columnconfigure(0, weight=1)

    def _browse_file(self):
        """Abre a janela de seleção de arquivo."""
        file_path = filedialog.askopenfilename(
            title=self.title, filetypes=self.file_types
        )

        if file_path:
            self.selected_path.set(file_path)

    def get_path(self):
        """
        Obtém o caminho selecionado.

        Returns:
            str: O caminho selecionado.
        """
        return self.selected_path.get()

    def set_path(self, path):
        """
        Define o caminho no seletor.

        Args:
            path (str): Caminho a ser definido.
        """
        self.selected_path.set(path)


class DirectorySelector(ttk.Frame):
    """Widget para seleção de diretórios."""

    def __init__(self, parent, title='Selecione um diretório', **kwargs):
        """
        Inicializa o seletor de diretórios.

        Args:
            parent: Widget pai.
            title (str, optional): Título da janela de seleção.
            **kwargs: Argumentos adicionais para o Frame.
        """
        super().__init__(parent, style='Card.TFrame', padding=10, **kwargs)

        self.title = title
        self.selected_path = tk.StringVar()

        self._create_widgets()

    def _create_widgets(self):
        """Cria os widgets do seletor de diretórios."""
        # Label descritiva
        ttk.Label(self, text=self.title, style='Bold.TLabel').pack(
            anchor='w', pady=(0, 5)
        )

        # Frame para o campo e botão
        input_frame = ttk.Frame(self)
        input_frame.pack(fill='x', expand=True)

        # Campo de texto para exibir o caminho
        self.path_entry = ttk.Entry(
            input_frame,
            textvariable=self.selected_path,
            width=50,
            style='Modern.TEntry',
        )
        self.path_entry.grid(row=0, column=0, padx=(0, 5), pady=5, sticky='we')

        # Botão para selecionar diretório
        self.browse_button = ModernButton(
            input_frame,
            text='Procurar...',
            command=self._browse_directory,
            width=12,
        )
        self.browse_button.grid(row=0, column=1, padx=5, pady=5)

        # Configurar o grid para expansão
        input_frame.columnconfigure(0, weight=1)

    def _browse_directory(self):
        """Abre a janela de seleção de diretório."""
        dir_path = filedialog.askdirectory(title=self.title)

        if dir_path:
            self.selected_path.set(dir_path)

    def get_path(self):
        """
        Obtém o diretório selecionado.

        Returns:
            str: O diretório selecionado.
        """
        return self.selected_path.get()

    def set_path(self, path):
        """
        Define o diretório no seletor.

        Args:
            path (str): Diretório a ser definido.
        """
        self.selected_path.set(path)


class StatusBar(ttk.Frame):
    """Barra de status para exibir mensagens ao usuário."""

    def __init__(self, parent, **kwargs):
        """
        Inicializa a barra de status.

        Args:
            parent: Widget pai.
            **kwargs: Argumentos adicionais para o Frame.
        """
        super().__init__(parent, style='StatusBar.TFrame', **kwargs)

        self.message = tk.StringVar()
        self._create_widgets()

    def _create_widgets(self):
        """Cria os widgets da barra de status."""
        self.label = ttk.Label(
            self,
            textvariable=self.message,
            anchor='w',
            style='StatusBar.TLabel',
        )
        self.label.pack(fill='x', padx=10, pady=5)

    def set_message(self, message):
        """
        Define uma mensagem na barra de status.

        Args:
            message (str): Mensagem a ser exibida.
        """
        self.message.set(message)
        self.update_idletasks()

    def clear(self):
        """Limpa a mensagem da barra de status."""
        self.message.set('')
        self.update_idletasks()


class ProcessingTab(ttk.Frame):
    """Base para abas de processamento na interface."""

    def __init__(self, parent, title='Processamento', **kwargs):
        """
        Inicializa a aba de processamento.

        Args:
            parent: Widget pai.
            title (str, optional): Título da aba.
            **kwargs: Argumentos adicionais para o Frame.
        """
        super().__init__(parent, style='Tab.TFrame', padding='15', **kwargs)

        self.title = title
        self.status_var = tk.StringVar()

        self._create_base_layout()

    def _create_base_layout(self):
        """Cria o layout básico da aba de processamento."""
        # Frame para os controles
        self.controls_frame = ttk.LabelFrame(
            self, text='Controles', style='Card.TLabelframe', padding=(15, 10)
        )
        self.controls_frame.pack(fill='x', expand=False, padx=10, pady=10)

        # Frame para as opções
        self.options_frame = ttk.LabelFrame(
            self, text='Opções', style='Card.TLabelframe', padding=(15, 10)
        )
        self.options_frame.pack(fill='x', expand=False, padx=10, pady=10)

        # Frame para o status
        self.status_frame = ttk.Frame(self, style='Card.TFrame', padding=10)
        self.status_frame.pack(fill='x', expand=False, padx=10, pady=10)

        # Barra de progresso estilizada
        self.progress = ttk.Progressbar(
            self.status_frame,
            orient='horizontal',
            mode='indeterminate',
            style='Modern.Horizontal.TProgressbar',
        )
        self.progress.pack(fill='x', padx=5, pady=10)

        # Label de status
        self.status_label = ttk.Label(
            self.status_frame,
            textvariable=self.status_var,
            style='StatusInfo.TLabel',
        )
        self.status_label.pack(padx=5, pady=5)

    def set_status(self, message):
        """
        Define uma mensagem na barra de status.

        Args:
            message (str): Mensagem a ser exibida.
        """
        self.status_var.set(message)
        self.update_idletasks()

    def start_progress(self):
        """Inicia a animação da barra de progresso."""
        self.progress.start()
        self.update_idletasks()

    def stop_progress(self):
        """Para a animação da barra de progresso."""
        self.progress.stop()
        self.update_idletasks()
