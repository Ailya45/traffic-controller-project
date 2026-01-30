import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import time
import datetime
import random
import os

# ==========================================
# 1. LÓGICA DE BLOQUEO (BIBLIOTECA)
# ==========================================
class FairRWLock:
    def __init__(self):
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.readers = 0
        self.writing = False
        self.writers_waiting = 0

    def acquire_read(self):
        with self.condition:
            while self.writing or self.writers_waiting > 0:
                self.condition.wait()
            self.readers += 1

    def release_read(self):
        with self.condition:
            self.readers -= 1
            if self.readers == 0:
                self.condition.notify_all()

    def acquire_write(self):
        with self.condition:
            self.writers_waiting += 1
            while self.writing or self.readers > 0:
                self.condition.wait()
            self.writers_waiting -= 1
            self.writing = True

    def release_write(self):
        with self.condition:
            self.writing = False
            self.condition.notify_all()

# ==========================================
# 2. INTERFAZ GRÁFICA MEJORADA
# ==========================================
class AppConcurrencia:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Bloqueo Justo de Archivos")
        self.root.geometry("900x700")  # Ventana más ancha para la gráfica
        
        # Configurar colores modernos
        self.root.configure(bg="#f0f2f5")

        try:
            self.root.iconbitmap("app.ico")
        except:
            # Si no encuentra el ícono, continuar sin él
            pass
        
        self.rw_lock = FairRWLock()
        self.file_name = "archivo_critico.txt"
        
        # Contadores para estadísticas
        self.active_readers = 0
        self.active_writers = 0
        self.total_readers = 0
        self.total_writers = 0
        self.history = []  # Historial para la gráfica
        self.max_history = 20  # Máximo de puntos en la gráfica

        # Limpiar archivo al iniciar
        if os.path.exists(self.file_name):
            os.remove(self.file_name)

        # Frame principal
        self.main_frame = tk.Frame(self.root, bg="#f0f2f5")
        
        # Cabecera con diseño moderno
        header_frame = tk.Frame(self.main_frame, bg="#ffffff", height=70)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Botón para volver al menú con diseño mejorado
        self.back_button = tk.Button(header_frame, text="← Menú", 
                                    bg="#4a5568", fg="white",
                                    font=("Arial", 9, "bold"),
                                    relief="flat",
                                    padx=15, pady=5,
                                    command=self.back_to_menu)
        self.back_button.place(x=15, y=20)
        
        # Título centrado
        tk.Label(header_frame, text="SIMULADOR DE BLOQUEO DE ARCHIVOS", 
                font=("Arial", 16, "bold"), 
                bg="#ffffff", fg="#2d3748").place(relx=0.5, rely=0.5, anchor="center")

        # Contenedor principal para visualización y gráfica
        main_container = tk.Frame(self.main_frame, bg="#f0f2f5")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Frame izquierdo para el archivo
        left_frame = tk.Frame(main_container, bg="#f0f2f5", width=500)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Frame derecho para la gráfica
        right_frame = tk.Frame(main_container, bg="#f0f2f5", width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        # ========== TARJETA DE VISUALIZACIÓN (IZQUIERDA) ==========
        card_visual = tk.Frame(left_frame, bg="#ffffff", relief="flat")
        card_visual.pack(fill=tk.BOTH, expand=True)
        
        # Título de la tarjeta
        tk.Label(card_visual, text="Visualización del archivo", 
                font=("Arial", 12, "bold"),
                bg="#ffffff", fg="#2d3748").pack(anchor="w", padx=20, pady=(15, 10))
        
        # Canvas con borde sutil
        canvas_container = tk.Frame(card_visual, bg="#e2e8f0", padx=2, pady=2)
        canvas_container.pack(padx=20, pady=(0, 15), fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_container, width=450, height=200, 
                               bg="#ffffff", 
                               highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Archivo con diseño moderno
        self.file_x1, self.file_y1 = 100, 50
        self.file_x2, self.file_y2 = 350, 160
        self.canvas.create_rectangle(self.file_x1, self.file_y1, self.file_x2, self.file_y2, 
                                    fill="#f8fafc", 
                                    outline="#4c51bf", 
                                    width=3)
        self.canvas.create_text(225, 25, 
                               text="ARCHIVO CRÍTICO", 
                               font=("Arial", 11, "bold"), 
                               fill="#4c51bf")
        
        # Leyenda con diseño mejorado
        legend_frame = tk.Frame(card_visual, bg="#ffffff")
        legend_frame.pack(pady=(0, 15), padx=20)
        
        tk.Label(legend_frame, text="Leyenda:", 
                font=("Arial", 9, "bold"),
                bg="#ffffff").grid(row=0, column=0, padx=(0, 15), sticky="w")
        
        # Indicador de lector
        reader_ind = tk.Frame(legend_frame, bg="#ffffff")
        reader_ind.grid(row=0, column=1, padx=10)
        tk.Label(reader_ind, text="⬤", fg="#4299e1",
                font=("Arial", 10),
                bg="#ffffff").pack(side=tk.LEFT)
        tk.Label(reader_ind, text="Lector",
                font=("Arial", 9),
                bg="#ffffff").pack(side=tk.LEFT, padx=3)
        
        # Indicador de escritor
        writer_ind = tk.Frame(legend_frame, bg="#ffffff")
        writer_ind.grid(row=0, column=2, padx=10)
        tk.Label(writer_ind, text="⬤", fg="#f56565",
                font=("Arial", 10),
                bg="#ffffff").pack(side=tk.LEFT)
        tk.Label(writer_ind, text="Escritor",
                font=("Arial", 9),
                bg="#ffffff").pack(side=tk.LEFT, padx=3)
        
        # Contadores en tiempo real
        stats_frame = tk.Frame(card_visual, bg="#ffffff")
        stats_frame.pack(pady=(0, 15), padx=20, fill=tk.X)
        
        self.reader_count_label = tk.Label(stats_frame, text="Lectores activos: 0", 
                                          font=("Arial", 9, "bold"), 
                                          bg="#ffffff", fg="#4299e1")
        self.reader_count_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.writer_count_label = tk.Label(stats_frame, text="Escritores activos: 0", 
                                          font=("Arial", 9, "bold"), 
                                          bg="#ffffff", fg="#f56565")
        self.writer_count_label.pack(side=tk.LEFT)

        # ========== TARJETA DE GRÁFICA (DERECHA) ==========
        card_graph = tk.Frame(right_frame, bg="#ffffff", relief="flat")
        card_graph.pack(fill=tk.BOTH, expand=True)
        
        # Título de la gráfica
        tk.Label(card_graph, text="📊Actividad en tiempo real", 
                font=("Arial", 12, "bold"),
                bg="#ffffff", fg="#2d3748").pack(anchor="w", padx=20, pady=(15, 10))
        
        # Canvas para la gráfica
        graph_container = tk.Frame(card_graph, bg="#edf2f7", padx=2, pady=2)
        graph_container.pack(padx=20, pady=(0, 15), fill=tk.BOTH, expand=True)
        
        self.graph_canvas = tk.Canvas(graph_container, width=250, height=250, 
                                     bg="#ffffff", 
                                     highlightthickness=0)
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Dibujar ejes de la gráfica
        self.draw_graph_axes()
        
        # Estadísticas totales
        totals_frame = tk.Frame(card_graph, bg="#ffffff")
        totals_frame.pack(pady=(0, 15), padx=20, fill=tk.X)
        
        tk.Label(totals_frame, text="Totales:", 
                font=("Arial", 9, "bold"),
                bg="#ffffff", fg="#2d3748").pack(anchor="w")
        
        self.total_readers_label = tk.Label(totals_frame, text="Lectores: 0", 
                                           font=("Arial", 9), 
                                           bg="#ffffff", fg="#4299e1")
        self.total_readers_label.pack(anchor="w", pady=(5, 2))
        
        self.total_writers_label = tk.Label(totals_frame, text="Escritores: 0", 
                                           font=("Arial", 9), 
                                           bg="#ffffff", fg="#f56565")
        self.total_writers_label.pack(anchor="w", pady=(2, 5))
        
        # Leyenda de la gráfica
        graph_legend = tk.Frame(card_graph, bg="#ffffff")
        graph_legend.pack(pady=(0, 15), padx=20)
        
        tk.Label(graph_legend, text="🟦 Lectores  🟥 Escritores", 
                font=("Arial", 8),
                bg="#ffffff", fg="#4a5568").pack()

        # ========== TARJETA DE CONTROLES ==========
        card_controls = tk.Frame(left_frame, bg="#ffffff", relief="flat")
        card_controls.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(card_controls, text="Control de hilos", 
                font=("Arial", 12, "bold"),
                bg="#ffffff", fg="#2d3748").pack(anchor="w", padx=20, pady=(15, 10))
        
        # Botones de control con diseño moderno
        btn_frame = tk.Frame(card_controls, bg="#ffffff")
        btn_frame.pack(padx=20, pady=(0, 15))
        
        # Botón Añadir Lector
        self.btn_reader = tk.Button(btn_frame, text="Añadir lector", 
                                   bg="#4299e1", fg="white", 
                                   font=("Arial", 11, "bold"),
                                   relief="flat",
                                   width=18, height=2,
                                   activebackground="#3182ce",
                                   activeforeground="white",
                                   command=self.spawn_reader)
        self.btn_reader.pack(side=tk.LEFT, padx=5)
        
        # Botón Añadir Escritor
        self.btn_writer = tk.Button(btn_frame, text="Añadir escritor", 
                                   bg="#f56565", fg="white", 
                                   font=("Arial", 11, "bold"),
                                   relief="flat",
                                   width=18, height=2,
                                   activebackground="#e53e3e",
                                   activeforeground="white",
                                   command=self.spawn_writer)
        self.btn_writer.pack(side=tk.LEFT, padx=5)

        # ========== TARJETA DE LOGS ==========
        card_logs = tk.Frame(self.main_frame, bg="#ffffff", relief="flat")
        card_logs.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Cabecera de logs con botón de limpiar
        log_header = tk.Frame(card_logs, bg="#2d3748")
        log_header.pack(fill=tk.X, padx=2, pady=2)
        
        # Título alineado a la izquierda
        tk.Label(log_header, text="Eventos del sistema", 
            font=("Arial", 11, "bold"),
            bg="#2d3748", fg="white").pack(side=tk.LEFT, padx=15, pady=8)
        
        # Frame para elementos derechos (contador y botón)
        header_right = tk.Frame(log_header, bg="#2d3748")
        header_right.pack(side=tk.RIGHT, padx=10, pady=8)
        
        # Contador de eventos
        self.event_count = 0
        self.event_label = tk.Label(header_right, text="Eventos: 0",
            font=("Arial", 9),
            bg="#2d3748",
            fg="#cbd5e0")
        self.event_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para limpiar logs VISIBLE en el header
        self.btn_clear = tk.Button(header_right, text="Limpiar Registros",
            bg="#718096", fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=12, pady=4,
            activebackground="#4a5568",
            activeforeground="white",
            command=self.clear_logs)
        self.btn_clear.pack(side=tk.LEFT)
        
        # Área de logs con scroll - REDUCIDA la altura para mejor visualización
        self.log_area = scrolledtext.ScrolledText(card_logs, 
            width=85, 
            height=8,  # Cambiado de 10 a 8
            bg="#1a202c", 
            fg="#e2e8f0", 
            font=("Consolas", 9),
            relief="flat",
            bd=0)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Configurar tags para el log con colores modernos
        self.log_area.tag_config("warning", foreground="#f6ad55")
        self.log_area.tag_config("reader", foreground="#63b3ed")
        self.log_area.tag_config("writer", foreground="#fc8181")
        self.log_area.tag_config("system", foreground="#a0aec0")
        
        # Iniciar actualización periódica de la gráfica
        self.update_graph()

    def draw_graph_axes(self):
        """Dibuja los ejes de la gráfica"""
        # Limpiar canvas
        self.graph_canvas.delete("all")
        
        # Dimensiones
        width = 250
        height = 250
        padding = 30
        
        # Dibujar ejes
        self.graph_canvas.create_line(padding, height - padding, width - padding, height - padding, fill="#cbd5e0")  # Eje X
        self.graph_canvas.create_line(padding, padding, padding, height - padding, fill="#cbd5e0")  # Eje Y
        
        # Etiquetas de ejes
        self.graph_canvas.create_text(padding - 10, padding, text="10", fill="#718096", font=("Arial", 7))
        self.graph_canvas.create_text(padding - 10, height - padding, text="0", fill="#718096", font=("Arial", 7))
        self.graph_canvas.create_text(width - padding + 10, height - padding + 10, text="Tiempo →", fill="#718096", font=("Arial", 7))
        self.graph_canvas.create_text(padding - 15, padding - 10, text="Hilos ↑", fill="#718096", font=("Arial", 7))
        
        # Línea de guía en 5 hilos
        mid_y = (height - 2 * padding) / 2 + padding
        self.graph_canvas.create_line(padding, mid_y, width - padding, mid_y, fill="#e2e8f0", dash=(2, 2))
        self.graph_canvas.create_text(padding - 10, mid_y, text="5", fill="#718096", font=("Arial", 7))

    def update_graph(self):
        """Actualiza la gráfica de actividad"""
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Agregar punto actual
        self.history.append((self.active_readers, self.active_writers))
        
        # Redibujar gráfica
        self.draw_graph_axes()
        
        # Dimensiones para dibujar
        width = 250
        height = 250
        padding = 30
        graph_width = width - 2 * padding
        graph_height = height - 2 * padding
        
        # Dibujar líneas de la gráfica
        if len(self.history) > 1:
            for i in range(1, len(self.history)):
                # Lectores (línea azul)
                x1 = padding + (i-1) * (graph_width / (self.max_history - 1))
                y1 = height - padding - (self.history[i-1][0] * (graph_height / 10))
                x2 = padding + i * (graph_width / (self.max_history - 1))
                y2 = height - padding - (self.history[i][0] * (graph_height / 10))
                
                self.graph_canvas.create_line(x1, y1, x2, y2, fill="#4299e1", width=2)
                
                # Escritores (línea roja)
                y1_w = height - padding - (self.history[i-1][1] * (graph_height / 10))
                y2_w = height - padding - (self.history[i][1] * (graph_height / 10))
                
                self.graph_canvas.create_line(x1, y1_w, x2, y2_w, fill="#f56565", width=2)
        
        # Actualizar contadores
        self.reader_count_label.config(text=f"Lectores activos: {self.active_readers}")
        self.writer_count_label.config(text=f"Escritores activos: {self.active_writers}")
        self.total_readers_label.config(text=f"Lectores totales: {self.total_readers}")
        self.total_writers_label.config(text=f"Escritores totales: {self.total_writers}")
        
        # Programar próxima actualización
        self.root.after(500, self.update_graph)

    # --- Herramientas Visuales ---
    def draw_thread(self, id, type):
        """Dibuja el hilo dentro del archivo en el Canvas."""
        color = "#4299e1" if type == "R" else "#f56565"
        # Posiciones aleatorias dentro de la zona del archivo
        x = random.randint(int(self.file_x1) + 20, int(self.file_x2) - 40)
        y = random.randint(int(self.file_y1) + 20, int(self.file_y2) - 40)
        
        tag = f"hilo_{id}"
        # Círculo del hilo con borde más fino
        self.canvas.create_oval(x, y, x+30, y+30, 
                               fill=color, 
                               outline="white", 
                               tags=tag, 
                               width=1)
        # Texto del hilo
        self.canvas.create_text(x+15, y+15, 
                               text=f"{type}{id}", 
                               fill="white", 
                               font=("Arial", 8, "bold"), 
                               tags=tag)
        return tag

    def write_log(self, text, tag=None):
        """Escribe en el log con formato de tiempo"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {text}\n", tag)
        self.event_count += 1
        self.event_label.config(text=f"Eventos: {self.event_count}")
        self.log_area.see(tk.END)

    def clear_logs(self):
        """Limpia la consola de eventos"""
        self.log_area.delete(1.0, tk.END)
        self.event_count = 0
        self.event_label.config(text=f"Eventos: {self.event_count}")
        self.write_log("Registro de eventos limpiado", "system")

    def back_to_menu(self):
        """Vuelve a la pantalla de inicio"""
        # Ocultar la aplicación principal
        self.main_frame.pack_forget()
        
        # Mostrar la pantalla de inicio
        if hasattr(self, 'start_screen'):
            self.start_screen.frame.pack(fill=tk.BOTH, expand=True)

    # --- Procesos de los Hilos ---
    def reader_task(self, id):
        self.write_log(f"Lector {id}: Esperando turno...", "reader")
        
        # Actualizar contadores
        self.total_readers += 1
        
        # 1. ACQUIRE (Bajo nivel)
        self.rw_lock.acquire_read()
        
        # 2. ENTRADA VISUAL
        tag = self.draw_thread(id, "R")
        self.active_readers += 1
        
        try:
            # Operación de archivo
            with open(self.file_name, "r") as f:
                content = f.readlines()
                last = content[-1].strip() if content else "Archivo vacío"
            self.write_log(f"→ Lector {id} LEYENDO: {last}", "reader")
            time.sleep(random.uniform(2, 4)) # Tiempo en sección crítica
        except Exception as e:
            self.write_log(f"Error Lector: {e}", "warning")
        finally:
            # 3. SALIDA VISUAL
            self.canvas.delete(tag)
            self.active_readers -= 1
            
            # 4. RELEASE (Bajo nivel)
            self.rw_lock.release_read()
            self.write_log(f"← Lector {id} salió.", "reader")

    def writer_task(self, id):
        self.write_log(f"ESCRITOR {id}: SOLICITANDO EXCLUSIVIDAD...", "writer")
        
        # Actualizar contadores
        self.total_writers += 1
        
        # 1. ACQUIRE (Bajo nivel)
        self.rw_lock.acquire_write()
        
        # 2. ENTRADA VISUAL
        tag = self.draw_thread(id, "W")
        self.active_writers += 1
        
        try:
            self.write_log(f"⚠️ ESCRITOR {id} ESCRIBIENDO ⚠️", "writer")
            with open(self.file_name, "a") as f:
                ahora = datetime.datetime.now().strftime("%H:%M:%S")
                f.write(f"Modificado por Escritor {id} a las {ahora}\n")
            time.sleep(3) # Tiempo en sección crítica
        except Exception as e:
            self.write_log(f"Error Escritor: {e}", "warning")
        finally:
            # 3. SALIDA VISUAL
            self.canvas.delete(tag)
            self.active_writers -= 1
            
            # 4. RELEASE (Bajo nivel)
            self.rw_lock.release_write()
            self.write_log(f"✓ ESCRITOR {id} liberó el archivo.", "writer")

    # --- Lanzadores ---
    def spawn_reader(self):
        r_id = random.randint(100, 999)
        threading.Thread(target=self.reader_task, args=(r_id,), daemon=True).start()

    def spawn_writer(self):
        w_id = random.randint(10, 99)
        threading.Thread(target=self.writer_task, args=(w_id,), daemon=True).start()

    def show(self):
        """Muestra el frame principal"""
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def set_start_screen(self, start_screen):
        """Establece referencia a la pantalla de inicio"""
        self.start_screen = start_screen


# ==========================================
# 3. PANTALLA DE INICIO MEJORADA
# ==========================================
class StartScreen:
    def __init__(self, root, app, support_url: str = "https://github.com/Ailya45/traffic-controller-project"):
        self.root = root
        self.app = app
        self.support_url = support_url

        self.frame = tk.Frame(self.root, bg="#f0f2f5")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Intentar cargar el ícono
        try:
            self.root.iconbitmap("app.ico")
        except:
            pass

        # Contenedor principal centrado
        container = tk.Frame(self.frame, bg="#f0f2f5")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Tarjeta principal
        main_card = tk.Frame(container, bg="#ffffff", padx=40, pady=40)
        main_card.pack()

        # Logo/Icono
        tk.Label(main_card, text="🔒", 
                font=("Arial", 48),
                bg="#ffffff",
                fg="#4c51bf").pack(pady=(0, 15))
        
        # Título principal
        tk.Label(main_card, text="SIMULADOR DE BLOQUEO", 
                font=("Arial", 20, "bold"),
                bg="#ffffff",
                fg="#2d3748").pack(pady=(0, 5))
        
        # Subtítulo
        tk.Label(main_card, text="Control de concurrencia para archivos", 
                font=("Arial", 11),
                bg="#ffffff",
                fg="#718096").pack(pady=(0, 30))

        # Botones principales
        btn_container = tk.Frame(main_card, bg="#ffffff")
        btn_container.pack()

        # Botón Iniciar
        btn_start = tk.Button(btn_container, text="Iniciar simulación", 
                             bg="#48bb78", fg="white", 
                             font=("Arial", 12, "bold"),
                             relief="flat",
                             width=25, height=2,
                             activebackground="#38a169",
                             activeforeground="white",
                             command=self.on_start)
        btn_start.grid(row=0, column=0, pady=8, padx=5)

        # Botón Ayuda
        btn_help = tk.Button(btn_container, text="Ayuda rápida", 
                            bg="#4299e1", fg="white", 
                            font=("Arial", 12, "bold"),
                            relief="flat",
                            width=25, height=2,
                            activebackground="#3182ce",
                            activeforeground="white",
                            command=self.show_help)
        btn_help.grid(row=1, column=0, pady=8, padx=5)

        # Botón Soporte
        btn_support = tk.Button(btn_container, text="Soporte técnico", 
                               bg="#9f7aea", fg="white", 
                               font=("Arial", 12, "bold"),
                               relief="flat",
                               width=25, height=2,
                               activebackground="#805ad5",
                               activeforeground="white",
                               command=self.on_support)
        btn_support.grid(row=2, column=0, pady=8, padx=5)

        # Botón Salir
        btn_exit = tk.Button(btn_container, text="Salir", 
                            bg="#f56565", fg="white", 
                            font=("Arial", 12, "bold"),
                            relief="flat",
                             width=25, height=2,
                            activebackground="#e53e3e",
                            activeforeground="white",
                            command=self.on_exit)
        btn_exit.grid(row=3, column=0, pady=8, padx=5)

        # Información de pie
        footer_frame = tk.Frame(self.frame, bg="#f0f2f5")
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        tk.Label(footer_frame, text="Simulador educativo - Sistema de lectores/escritores \n Proyecto realizado por Jesus Vasquez, Bermys Santana y Jose Velazque", 
                font=("Arial", 9),
                bg="#f0f2f5",
                fg="#a0aec0").pack()

    def on_start(self):
        """Ocultar pantalla de inicio y mostrar la app principal"""
        self.frame.pack_forget()
        self.app.show()

    def show_help(self):
        """Muestra ayuda básica"""
        help_text = """
        SIMULADOR DE BLOQUEO DE ARCHIVOS
        
        Este programa simula el acceso concurrente a un archivo:
        
        • LECTORES (azul): Pueden leer simultáneamente
        • ESCRITORES (rojo): Acceso exclusivo
        
        Cómo usar:
        1. Usa los botones para añadir lectores/escritores
        2. Observa cómo interactúan en el archivo
        3. Revisa los eventos en la consola
        4. Mira la gráfica de actividad en tiempo real
        
        La simulación usa un bloqueo justo (fair lock)
        que evita la inanición de escritores.
        """
        messagebox.showinfo("Ayuda Rápida", help_text)

    def on_support(self):
        """Abrir link de soporte"""
        try:
            import webbrowser
            webbrowser.open(self.support_url)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el enlace: {e}")

    def on_exit(self):
        """Salir de la aplicación"""
        self.root.quit()


# ==========================================
# 4. PROGRAMA PRINCIPAL
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    
    # Crear la aplicación principal
    app = AppConcurrencia(root)
    
    # Crear pantalla de inicio
    start_screen = StartScreen(root, app, support_url="https://github.com/Ailya45/traffic-controller-project")
    
    # Establecer referencia recíproca
    app.set_start_screen(start_screen)
    
    root.mainloop()