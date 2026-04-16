import os
import random
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image, ImageTk
import io

class ReproductorMusical:
    def __init__(self, root):
        self.root = root
        self.root.title("Reproductor de Música - Proyecto Final")
        self.root.geometry("600x500")
        
        pygame.mixer.init()        
        
        self.lista_canciones = []
        self.indice_actual = 0
        self.modo_aleatorio = False
        self.modo_repetir = False
        self.reproduciendo = False
        
        self.archivo_auto_guardado = "ultima_sesion.json"

        self.crear_interfaz()

        self.cargar_sesion_automatica()

        self.actualizar_barra_progreso()

    def crear_interfaz(self):
        frame_superior = tk.Frame(self.root)
        frame_superior.pack(pady=10, fill="x", padx=10)
        
        frame_medio = tk.Frame(self.root)
        frame_medio.pack(pady=10, fill="both", expand=True, padx=10)
        
        frame_inferior = tk.Frame(self.root)
        frame_inferior.pack(pady=10, fill="x", padx=10)

        tk.Button(frame_superior, text="Cargar Carpeta", command=self.cargar_carpeta).pack(side="left", padx=5)
        tk.Button(frame_superior, text="Guardar Playlist", command=self.guardar_playlist).pack(side="left", padx=5)
        tk.Button(frame_superior, text="Cargar Playlist", command=self.cargar_playlist).pack(side="left", padx=5)

        self.listbox = tk.Listbox(frame_medio, width=40)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.seleccionar_cancion)

        frame_info = tk.Frame(frame_medio, width=200)
        frame_info.pack(side="right", fill="y", padx=10)
        
        self.label_caratula = tk.Label(frame_info, text="Sin Carátula", bg="gray", width=20, height=10)
        self.label_caratula.pack(pady=5)
        
        self.label_titulo = tk.Label(frame_info, text="Título: ---", font=("Arial", 10, "bold"))
        self.label_titulo.pack()
        self.label_artista = tk.Label(frame_info, text="Artista: ---")
        self.label_artista.pack()
        self.label_album = tk.Label(frame_info, text="Álbum: ---")
        self.label_album.pack()

        self.barra_progreso = ttk.Progressbar(frame_inferior, orient="horizontal", length=400, mode="determinate")
        self.barra_progreso.pack(pady=5)
        
        self.label_tiempo = tk.Label(frame_inferior, text="00:00 / 00:00")
        self.label_tiempo.pack()

        frame_controles = tk.Frame(frame_inferior)
        frame_controles.pack(pady=5)
        
        tk.Button(frame_controles, text="⏮ Anterior", command=self.anterior).pack(side="left", padx=5)
        tk.Button(frame_controles, text="▶ Play", command=self.reproducir).pack(side="left", padx=5)
        tk.Button(frame_controles, text="⏸ Pausa", command=self.pausar).pack(side="left", padx=5)
        tk.Button(frame_controles, text="⏹ Stop", command=self.stop).pack(side="left", padx=5)
        tk.Button(frame_controles, text="⏭ Siguiente", command=self.siguiente).pack(side="left", padx=5)

        frame_extras = tk.Frame(frame_inferior)
        frame_extras.pack(pady=5)
        
        self.btn_aleatorio = tk.Button(frame_extras, text="Aleatorio: OFF", command=self.toggle_aleatorio)
        self.btn_aleatorio.pack(side="left", padx=5)
        
        self.btn_repetir = tk.Button(frame_extras, text="Repetir: OFF", command=self.toggle_repetir)
        self.btn_repetir.pack(side="left", padx=5)
        
        tk.Label(frame_extras, text="Volumen:").pack(side="left", padx=5)
        self.slider_volumen = ttk.Scale(frame_extras, from_=0, to=1, orient="horizontal", command=self.cambiar_volumen)
        self.slider_volumen.set(0.5)
        self.slider_volumen.pack(side="left")
    
    def agregar_archivos(self):
        archivos = filedialog.askopenfilenames(filetypes=[("Archivos MP3", "*.mp3")])
        if archivos:
            for ruta in archivos:
                info = self.extraer_metadatos(ruta)
                self.lista_canciones.append(info)
                self.listbox.insert(tk.END, f"{info['artista']} - {info['titulo']}")

            self.guardar_sesion_automatica()

    def limpiar_lista(self):
        self.lista_canciones.clear()
        self.listbox.delete(0, tk.END)
        pygame.mixer.music.stop()
        self.guardar_sesion_automatica()

    def cargar_carpeta(self):
        carpeta = filedialog.askdirectory()
        if not carpeta:
            return  
        
        self.lista_canciones.clear()
        self.listbox.delete(0, tk.END)
        
        for archivo in os.listdir(carpeta):
            if archivo.endswith(".mp3"):
                ruta_completa = os.path.join(carpeta, archivo)
                info = self.extraer_metadatos(ruta_completa)
                self.lista_canciones.append(info)
                texto_lista = f"{info['artista']} - {info['titulo']}"
                self.listbox.insert(tk.END, texto_lista)

        self.guardar_sesion_automatica()

    def extraer_metadatos(self, ruta):
        info = {
            "ruta": ruta,
            "titulo": os.path.basename(ruta).replace(".mp3", ""),
            "artista": "Desconocido",
            "album": "Desconocido",
            "duracion": 0
        }
        try:
            audio = MP3(ruta, ID3=ID3)
            info["duracion"] = audio.info.length
            
            # Leer etiquetas ID3
            if audio.tags:
                if 'TIT2' in audio.tags:
                    info["titulo"] = str(audio.tags['TIT2'])
                if 'TPE1' in audio.tags:
                    info["artista"] = str(audio.tags['TPE1'])
                if 'TALB' in audio.tags:
                    info["album"] = str(audio.tags['TALB'])
        except Exception as e:
            print(f"Error leyendo {ruta}: {e}")
            
        return info

    def seleccionar_cancion(self, event):
        seleccion = self.listbox.curselection()
        if seleccion:
            self.indice_actual = seleccion[0]
            self.reproducir()

    def reproducir(self):
        if not self.lista_canciones:
            return
            
        cancion = self.lista_canciones[self.indice_actual]
        pygame.mixer.music.load(cancion["ruta"])
        pygame.mixer.music.play()
        self.reproduciendo = True
        
        self.label_titulo.config(text=f"Título: {cancion['titulo']}")
        self.label_artista.config(text=f"Artista: {cancion['artista']}")
        self.label_album.config(text=f"Álbum: {cancion['album']}")
        self.mostrar_caratula(cancion["ruta"])
        
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.indice_actual)
        self.listbox.activate(self.indice_actual)

    def pausar(self):
        if self.reproduciendo:
            pygame.mixer.music.pause()
            self.reproduciendo = False
        else:
            pygame.mixer.music.unpause()
            self.reproduciendo = True
    
    def stop(self):
        if self.lista_canciones:
            pygame.mixer.music.play()
            self.reproduciendo = True

    def siguiente(self):
        if not self.lista_canciones: return
        
        if self.modo_aleatorio:
            self.indice_actual = random.randint(0, len(self.lista_canciones) - 1)
        else:
            self.indice_actual += 1
            if self.indice_actual >= len(self.lista_canciones):
                if self.modo_repetir:
                    self.indice_actual = 0
                else:
                    self.indice_actual = len(self.lista_canciones) - 1
                    self.stop()
                    return
        self.reproducir()

    def anterior(self):
        if not self.lista_canciones: return
        self.indice_actual -= 1
        if self.indice_actual < 0:
            self.indice_actual = 0
        self.reproducir()
    
    def mostrar_caratula(self, ruta):
        try:
            audio = MP3(ruta, ID3=ID3)
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    imagen_data = tag.data
                    img = Image.open(io.BytesIO(imagen_data))
                    img = img.resize((150, 150), Image.Resampling.LANCZOS)
                    self.img_tk = ImageTk.PhotoImage(img)
                    self.label_caratula.config(image=self.img_tk, text="")
                    return
            self.label_caratula.config(image="", text="Sin Carátula", bg="gray")
        except:
            self.label_caratula.config(image="", text="Sin Carátula", bg="gray")
    
    def cambiar_volumen(self, valor):
        pygame.mixer.music.set_volume(float(valor))

    def toggle_aleatorio(self):
        self.modo_aleatorio = not self.modo_aleatorio
        estado = "ON" if self.modo_aleatorio else "OFF"
        self.btn_aleatorio.config(text=f"Aleatorio: {estado}")

    def toggle_repetir(self):
        self.modo_repetir = not self.modo_repetir
        estado = "ON" if self.modo_repetir else "OFF"
        self.btn_repetir.config(text=f"Repetir: {estado}")

    def actualizar_barra_progreso(self):
        if pygame.mixer.music.get_busy() and self.reproduciendo:
            tiempo_actual = pygame.mixer.music.get_pos() / 1000
            cancion = self.lista_canciones[self.indice_actual]
            duracion_total = cancion["duracion"]
            
            if duracion_total > 0:
                porcentaje = (tiempo_actual / duracion_total) * 100
                self.barra_progreso["value"] = porcentaje
                
                m_act, s_act = divmod(int(tiempo_actual), 60)
                m_tot, s_tot = divmod(int(duracion_total), 60)
                self.label_tiempo.config(text=f"{m_act:02d}:{s_act:02d} / {m_tot:02d}:{s_tot:02d}")
                
                if tiempo_actual >= duracion_total - 1:
                    self.siguiente()

        self.root.after(1000, self.actualizar_barra_progreso)

    def guardar_playlist(self):
        if not self.lista_canciones:
            messagebox.showwarning("Aviso", "No hay canciones para guardar.")
            return
            
        ruta_archivo = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if ruta_archivo:
            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(self.lista_canciones, archivo, indent=4)
            messagebox.showinfo("Éxito", "Playlist guardada correctamente.")

    def cargar_playlist(self):
        ruta_archivo = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if ruta_archivo:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                self.lista_canciones = json.load(archivo)
            
            self.listbox.delete(0, tk.END)
            for info in self.lista_canciones:
                texto_lista = f"{info['artista']} - {info['titulo']}"
                self.listbox.insert(tk.END, texto_lista)
    
    def guardar_sesion_automatica(self):
        try:
            with open(self.archivo_auto_guardado, 'w', encoding='utf-8') as f:
                json.dump(self.lista_canciones, f, indent=4)
        except Exception as e:
            print(f"No se pudo auto-guardar: {e}")

    def cargar_sesion_automatica(self):
        """Si existe el archivo de la sesión anterior, lo carga apenas abre el programa."""
        if os.path.exists(self.archivo_auto_guardado):
            try:
                with open(self.archivo_auto_guardado, 'r', encoding='utf-8') as f:
                    self.lista_canciones = json.load(f)
                
                self.listbox.delete(0, tk.END)
                for info in self.lista_canciones:
                    self.listbox.insert(tk.END, f"{info['artista']} - {info['titulo']}")
            except:
                pass

if __name__ == "__main__":
    ventana = tk.Tk()
    app = ReproductorMusical(ventana)
    ventana.mainloop()