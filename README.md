# MSI Temp Monitor GUI

A Python desktop application to monitor CPU and GPU temperatures in real time using **LibreHardwareMonitor**, with logging, configurable alerts, and a statistical control chart — no third-party monitoring software required.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey) ![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- Real-time CPU and GPU temperature monitoring
- Configurable alert thresholds for CPU and GPU
- Adjustable polling interval (minimum 1 second)
- Automatic logging to CSV and TXT files
- Statistical Control Chart (X-bar with 3-sigma limits)
- Clean dark UI built with CustomTkinter
- No dependency on MSI Afterburner or any external monitoring app

---

## Project Structure

```
MSI-Temp-Monitor-GUI/
├── main.py          # Entry point
├── temp_reader.py   # Hardware sensor reading logic (LibreHardwareMonitor)
├── logger.py        # Log management (CSV + TXT)
├── ui.py            # GUI (CustomTkinter + Matplotlib)
├── dll/             # Required .NET DLLs
│   ├── LibreHardwareMonitorLib.dll
│   ├── HidSharp.dll
│   ├── System.Memory.dll
│   └── ...
└── logs/            # Auto-generated log files
    ├── temperaturas.csv
    └── temperaturas_log.txt
```

---

## Requirements

- Windows 10 or 11
- Python 3.10+
- Administrator privileges (required to access hardware sensors)

### Python dependencies

```bash
pip install pythonnet customtkinter matplotlib pandas
```

### DLL dependencies

Download the latest release of [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases) and copy all `.dll` files from the ZIP into the `dll/` folder.

> **Important:** After copying, right-click each `.dll` → Properties → check **Unblock** at the bottom of the General tab. Windows blocks DLLs downloaded from the internet by default.

---

## Installation

1. Clone or download this repository
2. Install Python dependencies:
   ```bash
   pip install pythonnet customtkinter matplotlib pandas
   ```
3. Download LibreHardwareMonitor and copy all `.dll` files into the `dll/` folder
4. Unblock all DLLs (see Requirements above)

---

## Usage

Run the application as **Administrator**:

```bash
python main.py
```

> Running as Administrator is required for LibreHardwareMonitor to access CPU temperature sensors.

### Controls

| Button | Description |
|---|---|
| ▶️ Start | Begin temperature monitoring |
| ⏹️ Stop | Stop monitoring |
| 📄 Records | View raw log history |
| 📈 Control Chart | View statistical control chart |

### Configuration

| Field | Description |
|---|---|
| GPU Threshold (C) | Temperature alert threshold for GPU |
| CPU Threshold (C) | Temperature alert threshold for CPU |
| Interval (s) | Polling interval in seconds (minimum: 1) |

---

## Logs

Logs are saved automatically to the `logs/` folder:

- `temperaturas.csv` — structured data with date, time, CPU and GPU temperatures
- `temperaturas_log.txt` — plain text log in the same format

The `logs/` folder is created automatically on first run.

---

## Control Chart

The Control Chart view displays a real-time statistical process control (SPC) chart with:

- Temperature series for CPU and GPU
- Center line (mean)
- Upper and lower control limits (UCL/LCL) at ±3 standard deviations
- Highlighted out-of-control points

---

## Troubleshooting

**CPU temperature shows 0.0°C**
Make sure you are running the script as Administrator. Some AMD Ryzen sensors require elevated privileges to be read.

**DLL load error / FileLoadException**
The DLL was blocked by Windows. Right-click the `.dll` file → Properties → Unblock.

**Missing DLL error on startup**
Copy all `.dll` files from the LibreHardwareMonitor ZIP into the `dll/` folder, not just `LibreHardwareMonitorLib.dll`.

**Import warning in VS Code**
The warning `Import "LibreHardwareMonitor.Hardware" could not be resolved` is expected — the editor cannot statically analyze .NET assemblies. Add `# type: ignore` to suppress it. The code runs correctly at runtime.

---

## Hardware Tested

| Component | Model |
|---|---|
| CPU | AMD Ryzen 7 5800H |
| GPU (iGPU) | AMD Radeon Graphics |
| GPU (dGPU) | NVIDIA GeForce RTX 3050 Ti Laptop |
| Laptop | MSI |

---

## Acknowledgements

- [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor) — hardware sensor library
- [pythonnet](https://github.com/pythonnet/pythonnet) — .NET/Python interop
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — modern UI framework
- [Matplotlib](https://matplotlib.org/) — charting library
