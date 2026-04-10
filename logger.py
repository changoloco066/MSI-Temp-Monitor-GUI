import os
import csv
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LOG_CSV = os.path.join(LOG_DIR, "temperaturas.csv")
LOG_TXT = os.path.join(LOG_DIR, "temperaturas_log.txt")

def init_logs():
    os.makedirs(LOG_DIR, exist_ok=True)
    if not os.path.exists(LOG_CSV):
        with open(LOG_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Fecha", "Hora", "CPU Temp (C)", "GPU Temp (C)"])  # sin °
    if not os.path.exists(LOG_TXT):
        with open(LOG_TXT, "w", encoding="utf-8") as f:
            f.write("Fecha,Hora,CPU Temp (C),GPU Temp (C)\n")  # sin °

def save(cpu: float, gpu: float):
    now = datetime.now()
    fecha = now.strftime("%Y-%m-%d")
    hora  = now.strftime("%H:%M:%S")
    row   = [fecha, hora, cpu, gpu]
    with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)
    with open(LOG_TXT, "a", encoding="utf-8") as f:
        f.write(f"{fecha},{hora},{cpu},{gpu}\n")

def read_logs() -> str:
    if not os.path.exists(LOG_TXT):
        return "No hay registros aún."
    with open(LOG_TXT, "r", encoding="utf-8") as f:
        return f.read()

def read_logs() -> str:
    if not os.path.exists(LOG_TXT):
        return "No hay registros aún."
    with open(LOG_TXT, "r") as f:
        return f.read()

def read_csv_data():
    import pandas as pd
    if not os.path.exists(LOG_CSV):
        return None
    df = pd.read_csv(LOG_CSV, encoding="latin1")
    df["CPU"] = pd.to_numeric(df["CPU Temp (C)"], errors="coerce")
    df["GPU"] = pd.to_numeric(df["GPU Temp (C)"], errors="coerce")
    return df