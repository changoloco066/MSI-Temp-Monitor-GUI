import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import logger

DEFAULT_INTERVAL_MS = 3000

class App(ctk.CTk):
    def __init__(self, reader):
        super().__init__()
        self.reader = reader
        self.monitoreando = False
        self.job_id = None

        self.title("Monitor de Temperaturas MSI")
        self.geometry("800x520")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._build_sidebar()
        self._build_main()

        logger.init_logs()

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=160)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(sidebar, text="Controles", font=("Segoe UI", 18, "bold")).pack(pady=15)
        ctk.CTkButton(sidebar, text="▶️ Iniciar",      command=self.iniciar).pack(pady=5, fill="x")
        ctk.CTkButton(sidebar, text="⏹️ Detener",      command=self.detener).pack(pady=5, fill="x")
        ctk.CTkButton(sidebar, text="📄 Registros",    command=self.ver_registros).pack(pady=5, fill="x")
        ctk.CTkButton(sidebar, text="📈 Control Chart",command=self.ver_control_chart).pack(pady=5, fill="x")

    def _build_main(self):
        main = ctk.CTkFrame(self)
        main.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        self.lbl_cpu = ctk.CTkLabel(main, text="🌡️ CPU: -- °C", font=("Segoe UI", 24))
        self.lbl_cpu.pack(pady=(10, 5))
        self.lbl_gpu = ctk.CTkLabel(main, text="🌡️ GPU: -- °C", font=("Segoe UI", 24))
        self.lbl_gpu.pack(pady=5)
        self.lbl_time = ctk.CTkLabel(main, text="🕒 Última actualización: --", font=("Segoe UI", 13))
        self.lbl_time.pack(pady=(0, 10))
        self.lbl_status = ctk.CTkLabel(main, text="🛈 Estado: Inactivo", font=("Segoe UI", 12))
        self.lbl_status.pack(pady=(0, 10))
        self._default_color = self.lbl_status.cget("text_color")

        ctk.CTkLabel(main, text="Umbral GPU (°C):", font=("Segoe UI", 12)).pack(anchor="w", padx=10)
        self.entry_umbral_gpu = ctk.CTkEntry(main, placeholder_text="Ej. 75")
        self.entry_umbral_gpu.pack(fill="x", padx=10, pady=(0, 5))

        ctk.CTkLabel(main, text="Umbral CPU (°C):", font=("Segoe UI", 12)).pack(anchor="w", padx=10)
        self.entry_umbral_cpu = ctk.CTkEntry(main, placeholder_text="Ej. 85")
        self.entry_umbral_cpu.pack(fill="x", padx=10, pady=(0, 5))

        ctk.CTkLabel(main, text="Intervalo (s):", font=("Segoe UI", 12)).pack(anchor="w", padx=10)
        self.entry_intervalo = ctk.CTkEntry(main, placeholder_text="Min 1, por defecto 3")
        self.entry_intervalo.pack(fill="x", padx=10, pady=(0, 15))

        self.frame_dinamico = ctk.CTkFrame(main)
        self.frame_dinamico.pack(expand=True, fill="both", pady=5, padx=10)

    # --- Monitoreo ---

    def iniciar(self):
        if not self.monitoreando:
            self.monitoreando = True
            self.lbl_status.configure(text="🔥 Monitoreando", text_color=self._default_color)
            self._ciclo()
        else:
            self.lbl_status.configure(text="⚠️ Ya está monitoreando")

    def detener(self):
        if self.monitoreando:
            self.monitoreando = False
            if self.job_id:
                self.after_cancel(self.job_id)
            self.lbl_status.configure(text="⏹️ Monitoreo detenido")
        else:
            self.lbl_status.configure(text="⚠️ No estaba monitoreando")

    def _ciclo(self):
        if not self.monitoreando:
            return
        try:
            temps = self.reader.read()
            cpu = temps.get("CPU")
            gpu = temps.get("GPU")

            self.lbl_cpu.configure(text=f"🌡️ CPU: {cpu:.1f} °C" if cpu is not None else "🌡️ CPU: N/A")
            self.lbl_gpu.configure(text=f"🌡️ GPU: {gpu:.1f} °C" if gpu is not None else "🌡️ GPU: N/A")
            self.lbl_time.configure(text=f"🕒 Última actualización: {datetime.now():%Y-%m-%d %H:%M:%S}")
            self.lbl_status.configure(text="✅ Monitoreando", text_color=self._default_color)

            if cpu is not None and gpu is not None:
                logger.save(cpu, gpu)

            # Alertas
            self._check_alert("GPU", gpu, self.entry_umbral_gpu)
            self._check_alert("CPU", cpu, self.entry_umbral_cpu)

        except Exception as e:
            self.lbl_status.configure(text=f"❌ Error: {e}", text_color="red")

        try:
            secs = max(1.0, float(self.entry_intervalo.get()))
        except ValueError:
            secs = DEFAULT_INTERVAL_MS / 1000
        self.job_id = self.after(int(secs * 1000), self._ciclo)

    def _check_alert(self, nombre, valor, entry):
        if valor is None:
            return
        try:
            umbral = float(entry.get())
        except ValueError:
            return
        if valor > umbral:
            self.lbl_status.configure(text=f"❗ {nombre} > {umbral}°C", text_color="red")
            root = tk.Tk(); root.withdraw()
            messagebox.showwarning(f"Alerta {nombre}", f"{nombre} alcanzó {valor:.1f}°C (umbral {umbral}°C)")
            root.destroy()

    # --- Vistas dinámicas ---

    def _limpiar_frame(self):
        for w in self.frame_dinamico.winfo_children():
            w.destroy()

    def ver_registros(self):
        self._limpiar_frame()
        texto = logger.read_logs()
        caja = ctk.CTkTextbox(self.frame_dinamico, wrap="none")
        caja.insert("1.0", texto)
        caja.configure(state="disabled")
        caja.pack(expand=True, fill="both", padx=5, pady=5)

    def ver_control_chart(self):
        self._limpiar_frame()
        df = logger.read_csv_data()
        if df is None or df.empty:
            ctk.CTkLabel(self.frame_dinamico, text="No hay datos suficientes.").pack(pady=20)
            return

        gpu_data = df["GPU"].dropna().values
        cpu_data = df["CPU"].dropna().values

        def stats(data):
            mu = data.mean()
            sigma = data.std(ddof=1)
            return mu, mu + 3*sigma, mu - 3*sigma

        mu_g, lcs_g, lci_g = stats(gpu_data)
        mu_c, lcs_c, lci_c = stats(cpu_data)

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)

        x_g = list(range(1, len(gpu_data)+1))
        x_c = list(range(1, len(cpu_data)+1))

        ax.plot(x_g, gpu_data, marker='o', linestyle='-', label='GPU Temp')
        ax.plot(x_c, cpu_data, marker='s', linestyle='-', label='CPU Temp')
        ax.axhline(mu_g,  linewidth=1.5, label='GPU Media')
        ax.axhline(lcs_g, linestyle='--', label='GPU LCS')
        ax.axhline(lci_g, linestyle='--')
        ax.axhline(mu_c,  linewidth=1.5, label='CPU Media')
        ax.axhline(lcs_c, linestyle='-.', label='CPU LCS')
        ax.axhline(lci_c, linestyle='-.')

        # Puntos fuera de control
        fa_x_g = [i+1 for i, v in enumerate(gpu_data) if v > lcs_g or v < lci_g]
        fa_y_g = [v for v in gpu_data if v > lcs_g or v < lci_g]
        fa_x_c = [i+1 for i, v in enumerate(cpu_data) if v > lcs_c or v < lci_c]
        fa_y_c = [v for v in cpu_data if v > lcs_c or v < lci_c]
        ax.scatter(fa_x_g, fa_y_g, s=60, zorder=5, label='GPU fuera control')
        ax.scatter(fa_x_c, fa_y_c, s=60, zorder=5, label='CPU fuera control')

        ax.set_title("Carta de Control: GPU vs CPU")
        ax.set_xlabel("Muestra")
        ax.set_ylabel("Temperatura (°C)")
        ax.set_ylim(0, 100)
        ax.legend(loc='upper right', fontsize=7)
        ax.grid(True, linestyle=':', linewidth=0.5)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_dinamico)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both", padx=5, pady=5)