"""
Configuração de tema moderno para a interface da aplicação.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

# Paleta de cores moderna
COLORS = {
    'primary': '#4361EE',      # Azul primário
    'primary_light': '#4895EF', # Azul mais claro
    'primary_dark': '#3F37C9',  # Azul mais escuro
    'secondary': '#FF007A',     # Rosa como cor de destaque
    'bg_main': '#F8F9FA',       # Fundo principal (quase branco)
    'bg_card': '#FFFFFF',       # Branco para cards
    'text': '#212529',          # Texto quase preto
    'text_secondary': '#6C757D', # Texto secundário cinza
    'border': '#DEE2E6',        # Bordas leves
    'success': '#38B000',       # Verde de sucesso
    'warning': '#FF9F1C',       # Laranja de aviso
    'error': '#FF0054'          # Vermelho de erro
}

def setup_modern_theme(root):
    """
    Configura um tema moderno para a aplicação.
    
    Args:
        root: Instância principal da aplicação (Tk).
    """
    style = ttk.Style(root)
    
    # Verificar e configurar o tema base
    available_themes = style.theme_names()
    preferred_themes = ['clam', 'alt', 'default']
    
    base_theme = None
    for theme in preferred_themes:
        if theme in available_themes:
            base_theme = theme
            break
    
    if base_theme:
        style.theme_use(base_theme)
    
    # Fontes
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(family="Segoe UI", size=10)
    
    text_font = tkfont.nametofont("TkTextFont")
    text_font.configure(family="Segoe UI", size=10)
    
    # Estilos de Frame
    style.configure("TFrame", background=COLORS['bg_main'])
    style.configure("Card.TFrame", background=COLORS['bg_card'], relief="flat")
    style.configure("StatusBar.TFrame", background=COLORS['bg_card'], relief="flat", borderwidth=1)
    style.configure("Tab.TFrame", background=COLORS['bg_main'])
    
    # LabelFrame
    style.configure(
        "Card.TLabelframe", 
        background=COLORS['bg_card'],
        borderwidth=1,
        relief="solid",
        bordercolor=COLORS['border']
    )
    style.configure(
        "Card.TLabelframe.Label", 
        background=COLORS['bg_main'],
        foreground=COLORS['primary'],
        font=('Segoe UI', 11, 'bold')
    )
    
    # Labels
    style.configure("TLabel", background=COLORS['bg_card'], font=('Segoe UI', 10))
    style.configure("Bold.TLabel", background=COLORS['bg_card'], font=('Segoe UI', 10, 'bold'))
    style.configure("StatusBar.TLabel", background=COLORS['bg_card'], foreground=COLORS['text_secondary'])
    style.configure("StatusInfo.TLabel", background=COLORS['bg_card'], foreground=COLORS['primary'], font=('Segoe UI', 9))
    
    # Entry
    style.configure("TEntry", borderwidth=1, fieldbackground="white")
    style.configure("Modern.TEntry", borderwidth=1, fieldbackground="white")
    style.map('Modern.TEntry', 
              fieldbackground=[('focus', 'white')], 
              bordercolor=[('focus', COLORS['primary'])])
    
    # Button
    style.configure(
        "TButton", 
        background=COLORS['primary'],
        foreground="white",
        borderwidth=0,
        relief="flat",
        font=('Segoe UI', 10)
    )
    style.map('TButton', 
              background=[('active', COLORS['primary_light'])],
              relief=[('active', 'flat')])
    
    # Notebook
    style.configure(
        "Modern.TNotebook", 
        background=COLORS['bg_main'],
        tabmargins=[2, 5, 2, 0],
        borderwidth=0
    )
    style.configure(
        "Modern.TNotebook.Tab", 
        background=COLORS['bg_card'],
        foreground=COLORS['text'],
        padding=[15, 5],
        borderwidth=0,
        font=('Segoe UI', 10)
    )
    style.map('Modern.TNotebook.Tab', 
              background=[('selected', COLORS['primary']), ('active', COLORS['primary_light'])],
              foreground=[('selected', 'white'), ('active', 'white')])
    
    # Progressbar
    style.configure(
        "Modern.Horizontal.TProgressbar", 
        troughcolor=COLORS['bg_main'],
        borderwidth=0,
        background=COLORS['primary']
    )
    
    # Radiobutton
    style.configure(
        "TRadiobutton", 
        background=COLORS['bg_card'],
        font=('Segoe UI', 10)
    )
    style.map('TRadiobutton',
              background=[('active', COLORS['bg_card'])],
              indicatorcolor=[('selected', COLORS['primary'])])
    
    # Checkbutton
    style.configure(
        "TCheckbutton", 
        background=COLORS['bg_card'],
        font=('Segoe UI', 10)
    )
    style.map('TCheckbutton',
              background=[('active', COLORS['bg_card'])],
              indicatorcolor=[('selected', COLORS['primary'])])
    
    # Scales/Sliders - Corrigido para evitar o erro "Invalid state name normal"
    style.configure(
        "Horizontal.TScale", 
        background=COLORS['bg_card'],
        troughcolor=COLORS['border'],
        sliderlength=15,
        sliderthickness=15
    )
    
    # Usar apenas estados válidos no mapeamento (sem "normal")
    style.map('Horizontal.TScale',
              background=[('active', COLORS['bg_card'])],
              troughcolor=[('active', COLORS['primary_light'])])

    # Configurar cores de fundo para a janela principal
    root.configure(background=COLORS['bg_main'])
