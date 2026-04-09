import os
import json
import pygame
from mutagen.easyid3 import EasyID3
from tkinter import *
from tkinter import ttk, filedialog

# --- CONFIGURACIÓN INICIAL ---
ARCHIVO_BD = "biblioteca.json"
pygame.mixer.init() # Iniciamos el motor de audio

# --- LÓGICA DE DATOS Y AUDIO ---

def extraer_metadatos(ruta_archivo):
    """Usa EasyID3 para leer el título y artista."""
    try:
        etiquetas = EasyID3(ruta_archivo)
        titulo = etiquetas.get('title', [os.path.basename(ruta_archivo)])[0]
        artista = etiquetas.get('artist', ["Artista Desconocido"])[0]
        return {"ruta": ruta_archivo, "titulo": titulo, "artista": artista, "duracion": "Desconocida"}
    except Exception as e:
        print(f"Aviso al leer etiquetas: {e}")
        return {"ruta": ruta_archivo, "titulo": os.path.basename(ruta_archivo), "artista": "Artista Desconocido", "duracion": "Desconocida"}

def guardar_en_json(datos_cancion):
    """Guarda o actualiza el archivo JSON con la nueva canción."""
    biblioteca = []
    if os.path.exists(ARCHIVO_BD):
        with open(ARCHIVO_BD, "r", encoding="utf-8") as archivo:
            try:
                biblioteca = json.load(archivo)
            except json.JSONDecodeError:
                biblioteca = []

    # Evitar duplicados
    for cancion in biblioteca:
        if cancion["ruta"] == datos_cancion["ruta"]:
            return # Ya existe, no la guardamos de nuevo

    biblioteca.append(datos_cancion)
    with open(ARCHIVO_BD, "w", encoding="utf-8") as archivo:
        json.dump(biblioteca, archivo, indent=4, ensure_ascii=False)
    print(f"✅ Guardado en JSON: {datos_cancion['titulo']}")

# --- FUNCIONES DE LOS BOTONES ---

def accion_play():
    """Abre el explorador, lee metadatos, guarda en JSON y reproduce."""
    # Abrir ventana para elegir archivo MP3
    ruta_archivo = filedialog.askopenfilename(
        title="Elige una canción", 
        filetypes=[("Archivos MP3", "*.mp3")]
    )
    
    if ruta_archivo:
        # 1. Extraer y guardar datos
        datos = extraer_metadatos(ruta_archivo)
        guardar_en_json(datos)
        
        # 2. Actualizar el texto en la pantalla
        lbl_cancion.config(text=f"{datos['titulo']}\n{datos['artista']}")
        
        # 3. Reproducir el audio
        pygame.mixer.music.load(ruta_archivo)
        pygame.mixer.music.play()

def accion_pause():
    """Pausa o reanuda la canción."""
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()

def accion_stop():
    """Detiene la música por completo."""
    pygame.mixer.music.stop()
    lbl_cancion.config(text="Reproducción detenida")

def accion_proximamente():
    """Para los botones Anterior y Siguiente (requieren sistema de listas)."""
    print("Función en desarrollo...")

def salir_pantalla_completa(event):
    """Cierra la aplicación de forma segura."""
    pygame.mixer.music.stop() # Apagar música al salir
    root.attributes("-fullscreen", False)
    root.destroy()

# --- INTERFAZ GRÁFICA (TKINTER) ---

root = Tk()
root.title("Reproductor")
root.attributes('-fullscreen', True)
root.configure(bg="#121212")
root.bind("<Escape>", salir_pantalla_completa)

# Estilos
style = ttk.Style()
style.theme_use('default') 
style.configure("Fondo.TFrame", background="#121212")
style.configure("Aviso.TLabel", background="#121212", foreground="gray", font=("Arial", 12))
style.configure("Info.TLabel", background="#121212", foreground="white", font=("Arial", 28, "bold"), justify="center")
style.configure("Spotify.TButton", background="#C80000", foreground="white", font=("Arial", 24), borderwidth=0, relief="flat")
style.map("Spotify.TButton", background=[("active", "#C71414")])
style.configure("Linea.TSeparator", background="#282828")

# Header (Aviso para salir)
aviso = ttk.Label(root, text="Presiona 'ESC' para salir", style="Aviso.TLabel")
aviso.pack(pady=20, side="top")

# Centro de la pantalla (Información de la canción)
frame_centro = ttk.Frame(root, style="Fondo.TFrame")
frame_centro.pack(expand=True)

lbl_cancion = ttk.Label(frame_centro, text="Ninguna canción seleccionada\nPresiona ▶ para cargar", style="Info.TLabel")
lbl_cancion.pack()

# --- BARRA INFERIOR DE CONTROLES ---
frame_inferior = ttk.Frame(root, style="Fondo.TFrame")
frame_inferior.pack(side="bottom", fill="x", pady=20)

separador = ttk.Separator(frame_inferior, orient="horizontal", style="Linea.TSeparator")
separador.pack(side="top", fill="x", padx=40, pady=(0, 20)) 

frame_controles = ttk.Frame(frame_inferior, style="Fondo.TFrame")
frame_controles.pack(side="top")

pixel_64 = PhotoImage(width=64, height=64)

# Lista de controles (Símbolo, Función a ejecutar)
controles = [
    ("⏮", accion_proximamente),
    ("▶", accion_play),
    ("⏸", accion_pause),
    ("⏹", accion_stop),
    ("⏭", accion_proximamente)
]

for simbolo, comando in controles:
    btn = ttk.Button(
        frame_controles,
        text=simbolo,
        image=pixel_64,
        compound="center", 
        style="Spotify.TButton",
        cursor="hand2",
        command=comando # ¡Aquí conectamos el botón con su función!
    )
    btn.pack(side="left", padx=15)

root.mainloop()