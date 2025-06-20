import os
from datetime import datetime
import pandas as pd
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Rutas y umbrales
csv_file = r"C:\Users\bigot\Escritorio\Temperaturas_MSI_AB\logs_msi_afterburner\temperaturasMSI.csv"
log_txt  = r"C:\Users\bigot\Escritorio\Temperaturas_MSI_AB\registros_app\temperaturas_log.txt"
umbral_gpu = 80
umbral_cpu = 86
ultima_modificacion = None
job_id = None
monitoreando = False

# Asegura existencia del log .txt
if not os.path.exists(log_txt):
    with open(log_txt, 'w') as f:
        f.write("Fecha,Hora,GPU Temp (°C),CPU Temp (°C)\n")

# --- Funciones de monitoreo ---

def monitorear_temperaturas():
    global ultima_modificacion, job_id, monitoreando
    if not monitoreando:
        return

    try:
        if os.path.exists(csv_file):
            mod = os.path.getmtime(csv_file)
            if mod != ultima_modificacion:
                ultima_modificacion = mod

                df = pd.read_csv(csv_file, sep=',', encoding='latin1', skiprows=2)
                df.columns = df.columns.str.strip()
                cols = ['GPU1 temperature', 'CPU temperature']
                if all(c in df.columns for c in cols):
                    last = df[cols].dropna().tail(1)
                    gpu = float(last['GPU1 temperature'].values[0])
                    cpu = float(last['CPU temperature'].values[0])

                    temperatura_gpu_label.configure(text=f"🌡️ GPU: {gpu:.1f} °C")
                    temperatura_cpu_label.configure(text=f"🌡️ CPU: {cpu:.1f} °C")
                    ultima_actualizacion_label.configure(
                        text=f"🕒 Última actualización: {datetime.now():%Y-%m-%d %H:%M:%S}"
                    )

                    # Guardar en TXT
                    linea = f"{datetime.now():%Y-%m-%d,%H:%M:%S},{gpu},{cpu}\n"
                    with open(log_txt, 'a') as f:
                        f.write(linea)
    except Exception as e:
        estado_label.configure(text=f"❌ Error: {e}")

    # Programar siguiente lectura
    job_id = app.after(30_000, monitorear_temperaturas)

def iniciar_monitoreo():
    global monitoreando
    if not monitoreando:
        monitoreando = True
        estado_label.configure(text="🔥 Monitoreo iniciado")
        monitorear_temperaturas()
    else:
        estado_label.configure(text="⚠️ Ya está monitoreando")

def detener_monitoreo():
    global monitoreando, job_id
    if monitoreando:
        monitoreando = False
        if job_id:
            app.after_cancel(job_id)
        estado_label.configure(text="⏹️ Monitoreo detenido")
    else:
        estado_label.configure(text="⚠️ No estaba monitoreando")

# --- Funciones para frame dinámico ---

def limpiar_frame():
    for w in frame_dinamico.winfo_children():
        w.destroy()

def ver_registros():
    limpiar_frame()
    texto = "No se encontró el archivo de registros."
    if os.path.exists(log_txt):
        with open(log_txt, 'r') as f:
            texto = f.read()
    caja = ctk.CTkTextbox(frame_dinamico, wrap="none")
    caja.insert("1.0", texto)
    caja.configure(state="disabled")
    caja.pack(expand=True, fill="both", padx=10, pady=10)
def ver_estadisticas():
    limpiar_frame()

    if not os.path.exists(log_txt):
        ctk.CTkLabel(frame_dinamico, text="No se encontró el archivo de registros.").pack(pady=20)
        return

    # Leer y preparar datos
    df = pd.read_csv(log_txt)
    df['GPU Temp (°C)'] = pd.to_numeric(df['GPU Temp (°C)'], errors='coerce')
    df['CPU Temp (°C)'] = pd.to_numeric(df['CPU Temp (°C)'], errors='coerce')

    gpu_vals = {
        'Mínimo': df['GPU Temp (°C)'].min(),
        'Promedio': df['GPU Temp (°C)'].mean(),
        'Máximo': df['GPU Temp (°C)'].max()
    }
    cpu_vals = {
        'Mínimo': df['CPU Temp (°C)'].min(),
        'Promedio': df['CPU Temp (°C)'].mean(),
        'Máximo': df['CPU Temp (°C)'].max()
    }

    # Crear figura y eje
    fig = Figure(figsize=(5, 3), dpi=100)
    ax = fig.add_subplot(111)

    # Posiciones de las barras
    labels = list(gpu_vals.keys())
    x = range(len(labels))
    # Datos
    gpu_data = [gpu_vals[k] for k in labels]
    cpu_data = [cpu_vals[k] for k in labels]

    # Dibujar barras: grupo GPU a la izquierda, CPU a la derecha
    width = 0.35
    ax.bar([i - width/2 for i in x], gpu_data, width)  # GPU
    ax.bar([i + width/2 for i in x], cpu_data, width)  # CPU

    # Etiquetas y leyendas
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Temperatura (°C)")
    ax.set_title("Estadísticas GPU vs CPU")
    ax.legend(["GPU", "CPU"])

    #definir el limite de Y de 0 a 100 °C
    ax.set_ylim(0, 100)
    
    # Incrustar en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame_dinamico)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)


# --- GUI principal ---

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Monitor de Temperaturas MSI")
app.geometry("800x500")

# Sidebar de controles
frame_sidebar = ctk.CTkFrame(app, width=150)
frame_sidebar.pack(side="left", fill="y", padx=10, pady=10)

ctk.CTkLabel(frame_sidebar, text="Controles", font=("Segoe UI", 20, "bold")).pack(pady=15)
ctk.CTkButton(frame_sidebar, text="▶️ Iniciar",  command=iniciar_monitoreo).pack(pady=5, fill="x")
ctk.CTkButton(frame_sidebar, text="⏹️ Detener", command=detener_monitoreo).pack(pady=5, fill="x")
ctk.CTkButton(frame_sidebar, text="📄 Registros", command=ver_registros).pack(pady=5, fill="x")
ctk.CTkButton(frame_sidebar, text="📊 Estadísticas", command=ver_estadisticas).pack(pady=5, fill="x")

# Área principal de visualización
frame_contenido = ctk.CTkFrame(app)
frame_contenido.pack(side="right", expand=True, fill="both", padx=10, pady=10)

# Labels de estado en la parte superior del frame_contenido
temperatura_gpu_label = ctk.CTkLabel(frame_contenido, text="🌡️ GPU: -- °C", font=("Segoe UI", 24))
temperatura_gpu_label.pack(pady=(10,5))
temperatura_cpu_label = ctk.CTkLabel(frame_contenido, text="🌡️ CPU: -- °C", font=("Segoe UI", 24))
temperatura_cpu_label.pack(pady=5)
ultima_actualizacion_label = ctk.CTkLabel(
    frame_contenido, text="🕒 Última actualización: --", font=("Segoe UI", 14)
)
ultima_actualizacion_label.pack(pady=(0,15))
estado_label = ctk.CTkLabel(frame_contenido, text="🛈 Estado: Inactivo", font=("Segoe UI", 12))
estado_label.pack(pady=(0,10))

# Frame dinámico para registros/estadísticas
frame_dinamico = ctk.CTkFrame(frame_contenido)
frame_dinamico.pack(expand=True, fill="both", pady=10, padx=10)

app.mainloop()
