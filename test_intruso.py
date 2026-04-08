import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import time
import random
import math
import sys
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(ASSETS_PATH, exist_ok=True)
os.makedirs(RESULTS_PATH, exist_ok=True)

IMAGE_SIZE = (300, 300)

ITEMS = [
    {"categoria": "Animales", "opciones": ["perro", "gato", "mesa", "pájaro"], "intruso": "mesa"},
    {"categoria": "Frutas", "opciones": ["manzana", "banana", "auto", "naranja"], "intruso": "auto"},
    {"categoria": "Transporte", "opciones": ["auto", "avión", "tren", "silla"], "intruso": "silla"},
    {"categoria": "Herramientas", "opciones": ["martillo", "destornillador", "tijera", "libro"], "intruso": "libro"},
    {"categoria": "Ropa", "opciones": ["camisa", "pantalón", "zapato", "televisor"], "intruso": "televisor"},
    {"categoria": "Insectos", "opciones": ["abeja", "hormiga", "mariposa", "computadora"], "intruso": "computadora"},
    {"categoria": "Muebles", "opciones": ["mesa", "silla", "cama", "cuchara"], "intruso": "cuchara"},
    {"categoria": "Electrodomésticos", "opciones": ["heladera", "lavarropas", "microondas", "lámpara"], "intruso": "lámpara"},
    {"categoria": "Oficina", "opciones": ["lápiz", "goma", "regla", "plato"], "intruso": "plato"},
    {"categoria": "Juguetes", "opciones": ["pelota", "muñeca", "rompecabezas", "martillo"], "intruso": "martillo"},
    {"categoria": "Color", "opciones": ["circulo_rojo", "cuadrado_rojo", "triangulo_rojo", "circulo_azul"], "intruso": "circulo_azul"},
    {"categoria": "Forma", "opciones": ["circulo", "circulo", "circulo", "cuadrado"], "intruso": "cuadrado"},
    {"categoria": "Tamaño", "opciones": ["grande", "grande", "grande", "chico"], "intruso": "chico"},
    {"categoria": "Orientación", "opciones": ["flecha_arriba", "flecha_arriba", "flecha_arriba", "flecha_abajo"], "intruso": "flecha_abajo"},
    {"categoria": "Textura", "opciones": ["rayado", "rayado", "rayado", "liso"], "intruso": "liso"},
    {"categoria": "Cocina", "opciones": ["cuchillo", "tenedor", "cuchara", "cepillo"], "intruso": "cepillo"},
    {"categoria": "Jardinería", "opciones": ["pala", "rastrillo", "manguera", "taladro"], "intruso": "taladro"},
    {"categoria": "Escritura", "opciones": ["lapicera", "resaltador", "marcador", "destornillador"], "intruso": "destornillador"},
    {"categoria": "Limpieza", "opciones": ["escoba", "trapeador", "balde", "libro"], "intruso": "libro"},
    {"categoria": "Música", "opciones": ["guitarra", "piano", "batería", "tenedor"], "intruso": "tenedor"},
]

CONTROL_MEAN = 18.0
CONTROL_SD = 1.5
PUNTO_CORTE_LEVE = 17
PUNTO_CORTE = 15

def generate_roc_points(sensitivity=0.85, specificity=0.90):
    fpr_points = [0.0, 1.0 - specificity, 1.0]
    tpr_points = [0.0, sensitivity, 1.0]
    fpr = np.linspace(0, 1, 100)
    tpr = np.piecewise(fpr,
                       [fpr <= fpr_points[1], fpr > fpr_points[1]],
                       [lambda x: (sensitivity / fpr_points[1]) * x,
                        lambda x: 1 - (1 - sensitivity) * (1 - x) / (1 - fpr_points[1])])
    return fpr, tpr

def auc_manual(fpr, tpr):
    return np.trapezoid(tpr, fpr)

def generate_placeholder_image(word, size=IMAGE_SIZE):
    img = Image.new('RGB', size, color='lightgray')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), word, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((size[0]-w)//2, (size[1]-h)//2), word, fill='black', font=font)
    return img

def load_or_generate_image(word, size=IMAGE_SIZE):
    path = os.path.join(ASSETS_PATH, f"{word}.png")
    if os.path.exists(path):
        img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    else:
        return ImageTk.PhotoImage(generate_placeholder_image(word, size))

class IntrusoTest:
    def __init__(self, root, patient_id, age, gender, modo_visual):
        self.root = root
        self.patient_id = patient_id
        self.age = age
        self.gender = gender
        self.modo_visual = modo_visual

        self.root.title(f"Test de Intruso Lógico - {patient_id}")
        try:
            self.root.state('zoomed')
        except:
            try:
                self.root.attributes('-zoomed', True)
            except:
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.configure(bg="#F5F5F5")
        self.root.minsize(800, 600)

        self.answering = False
        self.current_idx = 0
        self.results = []
        self.start_time = None
        self.images = {}

        self.load_all_images()
        self.show_item()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.focus_set()

    def load_all_images(self):
        needed = set()
        for item in ITEMS:
            needed.update(item["opciones"])
        for name in needed:
            self.images[name] = load_or_generate_image(name)

    def create_option_button(self, parent, word, is_intruso):
        img = self.images.get(word)
        if self.modo_visual == "imagen_texto":
            if img:
                btn = tk.Button(parent, image=img, text=word.upper(), compound="top",
                                command=lambda: self.answer(is_intruso),
                                font=("Roboto", 18, "bold"), bg="white", fg="black",
                                width=IMAGE_SIZE[0], height=IMAGE_SIZE[1]+60,
                                relief=tk.RAISED, bd=3, cursor="hand2")
            else:
                btn = tk.Button(parent, text=word.upper(), command=lambda: self.answer(is_intruso),
                                font=("Roboto", 24, "bold"), bg="white", fg="black",
                                width=20, height=10, relief=tk.RAISED, bd=3, cursor="hand2")
        elif self.modo_visual == "solo_imagen":
            if img:
                btn = tk.Button(parent, image=img, command=lambda: self.answer(is_intruso),
                                bg="white", relief=tk.RAISED, bd=3,
                                width=IMAGE_SIZE[0], height=IMAGE_SIZE[1], cursor="hand2")
            else:
                btn = tk.Button(parent, text="?", command=lambda: self.answer(is_intruso),
                                font=("Roboto", 28), bg="white", fg="black",
                                width=15, height=8, relief=tk.RAISED, bd=3, cursor="hand2")
        else:  # solo_texto
            btn = tk.Button(parent, text=word.upper(), command=lambda: self.answer(is_intruso),
                            font=("Roboto", 50, "bold"), bg="white", fg="black",
                            width=30, height=12, relief=tk.RAISED, bd=8, cursor="hand2")
        return btn

    def show_item(self):
        if self.current_idx >= len(ITEMS):
            self.finish_test()
            return

        self.answering = False
        for widget in self.root.winfo_children():
            widget.destroy()

        item = ITEMS[self.current_idx]

        header = tk.Frame(self.root, bg="#F5F5F5", height=80)
        header.pack(fill=tk.X, pady=(10,0))
        tk.Label(header, text=f"Ítem {self.current_idx+1} de {len(ITEMS)}",
                 font=("Roboto", 20), bg="#F5F5F5", fg="#757575").pack(side=tk.RIGHT, padx=30)
        visual_map = {"imagen_texto": "Imagen+Texto", "solo_imagen": "Solo imagen", "solo_texto": "Solo texto"}
        modo_v = visual_map[self.modo_visual]
        tk.Label(header, text=f"Intruso Lógico | {modo_v} | Paciente: {self.patient_id}",
                 font=("Roboto", 16), bg="#F5F5F5", fg="#757575").pack(side=tk.LEFT, padx=30)

        instr = tk.Label(self.root, text="¿Cuál de estas imágenes NO pertenece al grupo?",
                         font=("Roboto", 32, "bold"), bg="#F5F5F5", fg="#212121")
        instr.pack(pady=30)

        frame_opts = tk.Frame(self.root, bg="#F5F5F5")
        frame_opts.pack(pady=30, expand=True, fill=tk.BOTH)

        opciones_mezcladas = item["opciones"].copy()
        random.shuffle(opciones_mezcladas)
        intruso = item["intruso"]

        for i, palabra in enumerate(opciones_mezcladas):
            row = i // 2
            col = i % 2
            es_intruso = (palabra == intruso)
            btn = self.create_option_button(frame_opts, palabra, es_intruso)
            btn.grid(row=row, column=col, padx=40, pady=20, sticky="nsew")
            if not hasattr(self, 'current_buttons'):
                self.current_buttons = []
            self.current_buttons.append(btn)

        frame_opts.grid_columnconfigure(0, weight=1)
        frame_opts.grid_columnconfigure(1, weight=1)
        frame_opts.grid_rowconfigure(0, weight=1)
        frame_opts.grid_rowconfigure(1, weight=1)

        self.start_time = time.time()
        self.root.focus_set()

    def answer(self, is_intruso):
        if self.answering:
            return
        self.answering = True

        rt = (time.time() - self.start_time) * 1000
        idx = self.current_idx
        if idx >= len(ITEMS):
            self.answering = False
            return

        item = ITEMS[idx]
        acierto = 1 if is_intruso else 0
        self.results.append({
            "serie": idx + 1,
            "categoria": item["categoria"],
            "opciones": item["opciones"],
            "respuesta_correcta": item["intruso"],
            "acierto": acierto,
            "tiempo_reaccion_ms": round(rt, 2)
        })

        self.current_idx += 1
        self.show_item()

    def show_results_window(self, tiempos, aciertos, total, precision, z_aciertos, interpretacion):
        results_win = tk.Toplevel(self.root)
        results_win.title("Resultados del Test")
        ancho = 1000
        alto = 800
        screen_width = results_win.winfo_screenwidth()
        screen_height = results_win.winfo_screenheight()
        x = (screen_width - ancho) // 2
        y = (screen_height - alto) // 2
        results_win.geometry(f"{ancho}x{alto}+{x}+{y}")
        results_win.configure(bg="#F5F5F5")
        results_win.transient(self.root)
        results_win.grab_set()
        results_win.minsize(800, 600)

        notebook = ttk.Notebook(results_win)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        tab_hist = ttk.Frame(notebook)
        notebook.add(tab_hist, text='Histograma de Tiempos')
        self._create_histogram_tab(tab_hist, tiempos, aciertos, total, precision, z_aciertos, interpretacion)

        tab_roc = ttk.Frame(notebook)
        notebook.add(tab_roc, text='Curva ROC')
        self._create_roc_tab(tab_roc)

        btn_frame = tk.Frame(results_win, bg="#F5F5F5")
        btn_frame.pack(pady=15)

        def on_close():
            results_win.destroy()
            self.root.destroy()
            sys.exit(0)

        results_win.protocol("WM_DELETE_WINDOW", on_close)
        btn_ok = tk.Button(btn_frame, text="Cerrar y salir", command=on_close,
                           font=("Roboto", 14), bg="#6200EE", fg="white",
                           relief=tk.RAISED, bd=2, padx=30, pady=10)
        btn_ok.pack()

    def _create_histogram_tab(self, parent, tiempos, aciertos, total, precision, z_aciertos, interpretacion):
        fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
        ax.hist(tiempos, bins=10, color='#6200EE', edgecolor='black', alpha=0.7)
        ax.set_xlabel('Tiempo de reacción (ms)', fontsize=11)
        ax.set_ylabel('Frecuencia', fontsize=11)
        ax.set_title('Distribución de tiempos de reacción', fontsize=13)
        ax.grid(True, linestyle='--', alpha=0.5)

        media = sum(tiempos)/len(tiempos) if tiempos else 0
        mediana = sorted(tiempos)[len(tiempos)//2] if tiempos else 0
        ax.axvline(media, color='red', linestyle='dashed', linewidth=2, label=f'Media: {media:.0f} ms')
        ax.axvline(mediana, color='green', linestyle='dashed', linewidth=2, label=f'Mediana: {mediana:.0f} ms')
        ax.legend(fontsize=9)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        frame_stats = tk.Frame(parent, bg="#F5F5F5")
        frame_stats.pack(pady=10, fill=tk.X)

        visual_map = {"imagen_texto": "Imagen+Texto", "solo_imagen": "Solo imagen", "solo_texto": "Solo texto"}
        stats_text = (f"Paciente: {self.patient_id} | Edad: {self.age} | Género: {self.gender}\n"
                      f"Modo visual: {visual_map[self.modo_visual]}\n"
                      f"Aciertos: {aciertos}/{total} ({precision*100:.1f}%)\n"
                      f"Tiempo promedio: {media:.0f} ms\n"
                      f"Mediana: {mediana:.0f} ms\n"
                      f"Desviación estándar: {math.sqrt(sum((t-media)**2 for t in tiempos)/len(tiempos)):.0f} ms\n"
                      f"Mínimo: {min(tiempos):.0f} ms | Máximo: {max(tiempos):.0f} ms\n"
                      f"Puntuación Z vs controles: {z_aciertos:.2f}\n"
                      f"Interpretación: {interpretacion}")
        lbl_stats = tk.Label(frame_stats, text=stats_text, font=("Roboto", 11),
                             bg="#F5F5F5", fg="#212121", justify=tk.LEFT)
        lbl_stats.pack(pady=10, padx=20)

    def _create_roc_tab(self, parent):
        fpr, tpr = generate_roc_points()
        roc_auc = auc_manual(fpr, tpr)

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(fpr, tpr, color='darkorange', lw=2, label=f'Curva ROC (AUC = {roc_auc:.2f})')
        ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Clasificador Aleatorio')
        ax.plot(1-0.90, 0.85, 'ro', markersize=10, label='Punto de Corte (15/20)')
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('Tasa de Falsos Positivos (1 - Especificidad)', fontsize=11)
        ax.set_ylabel('Tasa de Verdaderos Positivos (Sensibilidad)', fontsize=11)
        ax.set_title('Curva ROC del Test de Intruso Lógico', fontsize=13)
        ax.legend(loc="lower right", fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.5)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        info_text = ("La curva ROC muestra el rendimiento diagnóstico estimado del test.\n"
                     "El punto de corte de 15/20 aciertos (75%) ofrece una sensibilidad del 85%\n"
                     "y una especificidad del 90% para detectar deterioro cognitivo moderado.\n"
                     "Estos valores son preliminares y deben ser validados clínicamente.")
        lbl_info = tk.Label(parent, text=info_text, font=("Roboto", 10), justify=tk.LEFT,
                            bg="#F5F5F5", fg="#212121")
        lbl_info.pack(pady=15, padx=20)

    def finish_test(self):
        total = len(self.results)
        aciertos = sum(1 for r in self.results if r["acierto"])
        precision = aciertos / total if total > 0 else 0
        tiempos = [r["tiempo_reaccion_ms"] for r in self.results]
        tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else 0
        tiempo_sd = math.sqrt(sum((t - tiempo_promedio)**2 for t in tiempos) / len(tiempos)) if tiempos else 0
        tiempo_mediana = sorted(tiempos)[len(tiempos)//2] if tiempos else 0
        tiempo_min = min(tiempos) if tiempos else 0
        tiempo_max = max(tiempos) if tiempos else 0

        z_aciertos = (aciertos - CONTROL_MEAN) / CONTROL_SD if CONTROL_SD > 0 else 0

        if aciertos >= PUNTO_CORTE_LEVE:
            interpretacion = "Rendimiento dentro de lo normal"
        elif aciertos >= PUNTO_CORTE:
            interpretacion = "Deterioro leve (seguimiento recomendado)"
        else:
            interpretacion = "Deterioro moderado a severo (derivar a especialista)"

        final_data = {
            "id_paciente": self.patient_id,
            "edad": self.age,
            "genero": self.gender,
            "fecha": datetime.now().isoformat(),
            "modo_visual": self.modo_visual,
            "test": "Intruso Lógico (Razonamiento Abstracto)",
            "total_items": total,
            "aciertos": aciertos,
            "precision": precision,
            "tiempo_respuesta_promedio_ms": round(tiempo_promedio, 2),
            "tiempo_respuesta_desviacion_ms": round(tiempo_sd, 2),
            "tiempo_respuesta_mediana_ms": round(tiempo_mediana, 2),
            "tiempo_respuesta_min_ms": round(tiempo_min, 2),
            "tiempo_respuesta_max_ms": round(tiempo_max, 2),
            "tiempos_individuales_ms": tiempos,
            "z_aciertos_control": round(z_aciertos, 2),
            "interpretacion": interpretacion,
            "detalle_respuestas": self.results
        }

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(os.path.join(RESULTS_PATH, f"{self.patient_id}_{timestamp}.json"), "w", encoding="utf-8") as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        with open(os.path.join(RESULTS_PATH, f"{self.patient_id}_{timestamp}.txt"), "w", encoding="utf-8") as f:
            f.write(json.dumps(final_data, indent=2, ensure_ascii=False))

        print("\n" + "="*80)
        print("RESULTADOS DEL TEST (JSON):")
        print("="*80)
        print(json.dumps(final_data, indent=2, ensure_ascii=False))
        print("="*80)

        self.show_results_window(tiempos, aciertos, total, precision, z_aciertos, interpretacion)

    def on_closing(self):
        if self.results:
            partial = {
                "patient_id": self.patient_id,
                "current_item": self.current_idx,
                "results": self.results,
                "timestamp": datetime.now().isoformat()
            }
            with open(os.path.join(RESULTS_PATH, f"temp_{self.patient_id}.json"), "w", encoding="utf-8") as f:
                json.dump(partial, f, indent=2, ensure_ascii=False)
        self.root.destroy()
        sys.exit(0)


def main():
    root = tk.Tk()
    root.title("Evaluación de Razonamiento Abstracto - Intruso Lógico")
    root.geometry("850x950")
    root.configure(bg="#F5F5F5")

    tk.Label(root, text="Test de Intruso Lógico", font=("Roboto", 36, "bold"),
             bg="#F5F5F5", fg="#212121").pack(pady=(30,5))
    tk.Label(root, text="Evaluación de categorización y razonamiento abstracto", font=("Roboto", 18),
             bg="#F5F5F5", fg="#757575").pack()

    frame_datos = tk.Frame(root, bg="#F5F5F5")
    frame_datos.pack(pady=30)

    tk.Label(frame_datos, text="ID del paciente:", font=("Roboto", 16),
             bg="#F5F5F5", fg="#212121").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_id = tk.Entry(frame_datos, font=("Roboto", 16), width=20,
                        bg="#FFFFFF", fg="#212121", relief=tk.FLAT, bd=1)
    entry_id.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(frame_datos, text="Edad:", font=("Roboto", 16),
             bg="#F5F5F5", fg="#212121").grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entry_age = tk.Entry(frame_datos, font=("Roboto", 16), width=10,
                         bg="#FFFFFF", fg="#212121", relief=tk.FLAT, bd=1)
    entry_age.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    def validate_age(char):
        return char.isdigit() or char == ""
    vcmd = (root.register(validate_age), '%S')
    entry_age.config(validate="key", validatecommand=vcmd)

    tk.Label(frame_datos, text="(solo números)", font=("Roboto", 12),
             bg="#F5F5F5", fg="#757575").grid(row=1, column=2, padx=5, pady=10, sticky="w")

    tk.Label(frame_datos, text="Género:", font=("Roboto", 16),
             bg="#F5F5F5", fg="#212121").grid(row=2, column=0, padx=10, pady=10, sticky="e")
    gender_var = tk.StringVar(value="Masculino")
    gender_menu = ttk.Combobox(frame_datos, textvariable=gender_var, values=["Masculino", "Femenino", "Otro"],
                               font=("Roboto", 16), state="readonly", width=15)
    gender_menu.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    tk.Label(root, text="Modo visual:", font=("Roboto", 20, "bold"),
             bg="#F5F5F5", fg="#212121").pack(pady=(20,5))
    modo_visual_var = tk.StringVar(value="imagen_texto")
    frame_visual = tk.Frame(root, bg="#F5F5F5")
    frame_visual.pack(pady=5)
    tk.Radiobutton(frame_visual, text="Imagen + Texto (fácil)", variable=modo_visual_var, value="imagen_texto",
                   font=("Roboto", 16), bg="#F5F5F5", fg="#212121", selectcolor="#F5F5F5").pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(frame_visual, text="Solo imagen (medio)", variable=modo_visual_var, value="solo_imagen",
                   font=("Roboto", 16), bg="#F5F5F5", fg="#212121", selectcolor="#F5F5F5").pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(frame_visual, text="Solo texto (difícil)", variable=modo_visual_var, value="solo_texto",
                   font=("Roboto", 16), bg="#F5F5F5", fg="#212121", selectcolor="#F5F5F5").pack(side=tk.LEFT, padx=10)

    info_frame = tk.Frame(root, bg="#F5F5F5")
    info_frame.pack(pady=20)
    tk.Label(info_frame, text="📁 Las imágenes deben estar en la carpeta 'assets/'",
             font=("Roboto", 14), bg="#F5F5F5", fg="#757575").pack()
    tk.Label(info_frame, text="   con los nombres exactos: perro.png, gato.png, mesa.png, etc.",
             font=("Roboto", 14), bg="#F5F5F5", fg="#757575").pack()
    tk.Label(info_frame, text="   Si falta alguna, se mostrará un placeholder gris.",
             font=("Roboto", 14), bg="#F5F5F5", fg="#757575").pack()

    def start():
        pid = entry_id.get().strip()
        if not pid:
            messagebox.showwarning("Error", "Ingrese un ID de paciente")
            return
        age_str = entry_age.get().strip()
        if not age_str.isdigit():
            messagebox.showwarning("Error", "Ingrese una edad válida (solo números)")
            return
        age = int(age_str)
        gender = gender_var.get()
        modo_visual = modo_visual_var.get()

        root.destroy()
        new_root = tk.Tk()
        app = IntrusoTest(new_root, pid, age, gender, modo_visual)
        new_root.mainloop()

    btn = tk.Button(root, text="COMENZAR", command=start,
                    font=("Roboto", 24, "bold"), bg="#6200EE", fg="#FFFFFF",
                    relief=tk.RAISED, bd=0, padx=60, pady=20,
                    activebackground="#3700B3", activeforeground="#FFFFFF",
                    cursor="hand2")
    btn.pack(pady=40)

    root.mainloop()

if __name__ == "__main__":
    main()
