from tkinter import *
from tkinter import ttk
import random
import pygame
from mutagen.easyid3 import EasyID3
import os
import json

def salir_pantalla_completa(event):
    root.attributes("-fullscreen", False)
    root.destroy()

root = Tk()
root.title("Reproductor")
root.attributes('-fullscreen', True)
root.configure(bg="#121212")

root.bind("<Escape>", salir_pantalla_completa)

style = ttk.Style()
style.theme_use('default') 

style.configure("Fondo.TFrame", background="#121212")
style.configure("Aviso.TLabel", background="#121212", foreground="gray", font=("Arial", 12))

style.configure(
    "Spotify.TButton", 
    background="#DA291C", 
    foreground="white", 
    font=("Arial", 24),
    borderwidth=0,
    relief="flat"
)
style.map(
    "Spotify.TButton", 
    background=[("active", "#c51b0f")]
)

aviso = ttk.Label(root, text="Presiona 'ESC' para salir", style="Aviso.TLabel")
aviso.pack(pady=20)

frame_controles = ttk.Frame(root, style="Fondo.TFrame")
frame_controles.pack(expand=True)

pixel_64 = PhotoImage(width=64, height=64)

controles = [
    ("⏮", "Anterior"),
    ("▶", "Play"),
    ("⏸", "Pause"),
    ("⏹", "Stop"),
    ("⏭", "Siguiente")
]

for simbolo, accion in controles:
    btn = ttk.Button(
        frame_controles,
        text=simbolo,
        image=pixel_64,
        compound="center", # Centra el texto sobre la imagen transparente de 64x64
        style="Spotify.TButton",
        cursor="hand2"
    )
    btn.pack(side="left", padx=15)

root.mainloop()