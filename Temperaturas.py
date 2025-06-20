import os
from datetime import datetime
import pandas as pd
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox


# Rutas y umbrales
csv_file = r"C:\Users\bigot\Escritorio\Temperaturas_MSI_AB\logs_msi_afterburner\temperaturasMSI.csv"
log_txt  = r"C:\Users\bigot\Escritorio\Temperaturas_MSI_AB\registros_app\temperaturas_log.txt"
umbral_gpu = 80
umbral_cpu = 86
ultima_modificacion = None
job_id = None
monitoreando = False
DEFAULT_INTERVAL_MS = 3_000

# Asegura existencia del log .txt
if not os.path.exists(log_txt):
    with open(log_txt, 'w') as f:
        f.write("Fecha,Hora,GPU Temp (°C),CPU Temp (°C)\n")

# --- Funciones de monitoreo ---

def show_alert(titulo, mensaje):
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning(titulo, mensaje)
    root.destroy()
    
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

                    # Actualizar etiquetas
                    temperatura_gpu_label.configure(text=f"🌡️ GPU: {gpu:.1f} °C")
                    temperatura_cpu_label.configure(text=f"🌡️ CPU: {cpu:.1f} °C")
                    ultima_actualizacion_label.configure(
                        text=f"🕒 Última actualización: {datetime.now():%Y-%m-%d %H:%M:%S}"
                    )
                    estado_label.configure(text="✅ Monitoreando", text_color=default_text_color)

                    # Guardar en TXT
                    linea = f"{datetime.now():%Y-%m-%d,%H:%M:%S},{gpu},{cpu}\n"
                    with open(log_txt, 'a') as f:
                        f.write(linea)

                    # — Leer umbrales personalizados —
                    try:
                        th_gpu = float(entry_umbral_gpu.get())
                    except ValueError:
                        th_gpu = None
                    try:
                        th_cpu = float(entry_umbral_cpu.get())
                    except ValueError:
                        th_cpu = None

                    # — Disparar alertas si supera—
                    if th_gpu is not None and gpu > th_gpu:
                        estado_label.configure(text=f"❗ GPU > {th_gpu}°C", text_color="red")
                        show_alert("Alerta GPU", f"La GPU alcanzó {gpu:.1f} °C (umbral {th_gpu} °C)")
                    if th_cpu is not None and cpu > th_cpu:
                        estado_label.configure(text=f"❗ CPU > {th_cpu}°C", text_color="red")
                        show_alert("Alerta CPU", f"El CPU alcanzó {cpu:.1f} °C (umbral {th_cpu} °C)")
    except Exception as e:
        estado_label.configure(text=f"❌ Error: {e}", text_color="red")

    # Programar siguiente lectura dada por el usuario si no usar 3 segundos por defecto entre cada lectura (minimo 1 sewgundo)
    try: 
        secs = float(entry_intervalo.get())
        if secs < 1:
            secs = 1    
        interval_ms = int(secs * 1000)
    except ValueError:
        interval_ms = DEFAULT_INTERVAL_MS

    job_id = app.after(interval_ms, monitorear_temperaturas)


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

def ver_estadisticas_control():
    limpiar_frame()
    
    # 1) Leer datos
    if not os.path.exists(log_txt):
        ctk.CTkLabel(frame_dinamico, text="No se encontró el archivo de registros.").pack(pady=20)
        return

    df = pd.read_csv(log_txt)
    # Asegurarnos de usar los nombres tal como están en el .txt
    df['GPU'] = pd.to_numeric(df['GPU Temp (°C)'], errors='coerce')
    df['CPU'] = pd.to_numeric(df['CPU Temp (°C)'], errors='coerce')
    
    gpu_data = df['GPU'].dropna().values
    cpu_data = df['CPU'].dropna().values
    n = max(len(gpu_data), len(cpu_data))
    x = list(range(1, n+1))

    # 2) Estadísticos GPU
    mu_g    = gpu_data.mean()
    sigma_g = gpu_data.std(ddof=1)
    LCS_g   = mu_g + 3*sigma_g
    LCI_g   = mu_g - 3*sigma_g

    # 3) Estadísticos CPU
    mu_c    = cpu_data.mean()
    sigma_c = cpu_data.std(ddof=1)
    LCS_c   = mu_c + 3*sigma_c
    LCI_c   = mu_c - 3*sigma_c

    # 4) Detectar puntos fuera de control
    fa_x_g = [i+1 for i, v in enumerate(gpu_data) if v > LCS_g or v < LCI_g]
    fa_y_g = [v   for v in gpu_data if v > LCS_g or v < LCI_g]
    fa_x_c = [i+1 for i, v in enumerate(cpu_data) if v > LCS_c or v < LCI_c]
    fa_y_c = [v   for v in cpu_data if v > LCS_c or v < LCI_c]

    # 5) Dibujar la figura
    fig = Figure(figsize=(6, 4), dpi=100)
    ax  = fig.add_subplot(111)

    # Series GPU y CPU
    ax.plot(x[:len(gpu_data)], gpu_data, marker='o', linestyle='-', label='GPU Temp')
    ax.plot(x[:len(cpu_data)], cpu_data, marker='s', linestyle='-', label='CPU Temp')

    # Líneas de control GPU
    ax.axhline(mu_g,   linewidth=1.5, label='GPU Media (LCC)')
    ax.axhline(LCS_g,  linestyle='--',  label='GPU LCS')
    ax.axhline(LCI_g,  linestyle='--')

    # Líneas de control CPU
    ax.axhline(mu_c,   linewidth=1.5, label='CPU Media (LCC)')
    ax.axhline(LCS_c,  linestyle='-.',  label='CPU LCS')
    ax.axhline(LCI_c,  linestyle='-.')

    # Puntos fuera de control
    ax.scatter(fa_x_g, fa_y_g, marker='o', s=60, zorder=5, label='GPU fuera de control')
    ax.scatter(fa_x_c, fa_y_c, marker='s', s=60, zorder=5, label='CPU fuera de control')

    # Etiquetas y límites
    ax.set_title("Carta de Control: GPU vs CPU")
    ax.set_xlabel("Muestra")
    ax.set_ylabel("Temperatura (°C)")
    ax.set_ylim(0, 100)  
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, linestyle=':', linewidth=0.5)

    # 6) Incrustar en la GUI
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
ctk.CTkButton(frame_sidebar, text="📈 Control Chart", command=ver_estadisticas_control).pack(pady=5, fill="x")


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
default_text_color = estado_label.cget("text_color")


# — Entradas de umbral dentro del frame_contenido —
ctk.CTkLabel(frame_contenido, text="Umbral GPU (°C):", font=("Segoe UI", 12)).pack(anchor="w", padx=10)
entry_umbral_gpu = ctk.CTkEntry(frame_contenido, placeholder_text="Ej. 75")
entry_umbral_gpu.pack(fill="x", padx=10, pady=(0,5))

ctk.CTkLabel(frame_contenido, text="Umbral CPU (°C):", font=("Segoe UI", 12)).pack(anchor="w", padx=10)
entry_umbral_cpu = ctk.CTkEntry(frame_contenido, placeholder_text="Ej. 80")
entry_umbral_cpu.pack(fill="x", padx=10, pady=(0,15))

#Intervalos de monitoreo
ctk.CTkLabel(frame_contenido, text="Intervalo (s):", font=("Segoe UI", 12)).pack(anchor="w", padx=10)
entry_intervalo = ctk.CTkEntry(frame_contenido, placeholder_text="Min 1, por defecto 3")
entry_intervalo.pack(fill="x", padx=10, pady=(2,15))

# Frame dinámico para registros/estadísticas
frame_dinamico = ctk.CTkFrame(frame_contenido)
frame_dinamico.pack(expand=True, fill="both", pady=10, padx=10)

app.mainloop()
