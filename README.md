# MSI-Temp-Monitor-GUI
A lightweight Python application with a modern CustomTkinter interface to monitor your GPU and CPU temperatures in real time, log them to a local TXT file, and visualize historical data with control-chart style graphs.

Prerequisites
MSI Afterburner
Install and run MSI Afterburner on Windows.
In Settings → Monitoring → check “Log history to file.”
Set the Log file path to something like C:\Path\To\temperaturasMSI.csv.
Ensure “Enable hardware monitoring” is on in the tray icon.
Python & Dependencies
Python 3.8+ installed.
From a terminal or VS Code console, run:
pip install pandas customtkinter matplotlib

Configuration
CSV from MSI Afterburner
Point Afterburner’s CSV output to a local folder outside of OneDrive or any syncing service.
Example:
C:\TempMonitor\logs\temperaturasMSI.csv
Warning: Do not open this CSV in Excel or any editor while the app is running—MSI Afterburner must be free to append new lines.

Application Paths
The script uses two paths at the top of the code:
csv_file  = r"C:\Users\<you>\TempMonitor\logs\temperaturasMSI.csv"
log_txt   = r"C:\Users\<you>\TempMonitor\registros\temperaturas_log.txt"
Change these two variables to match your own folders before running.

TXT Log File
On first run the app will auto-create:
C:\Users\<you>\TempMonitor\registros\temperaturas_log.txt
This file archives each timestamped reading and must also live outside OneDrive.

Running the App
Edit paths in the Python script to point at your CSV and desired log folder.
(Optional) In the GUI, set:
GPU / CPU thresholds for on-screen alerts.
Monitoring interval in seconds (minimum 1 s).
Click ▶️ Iniciar to start real-time monitoring.
Use “📄 Registros” to view the raw log, or “📈 Control Chart” to see historical min/mean/max control-chart.

Warnings
Do not keep this project folder inside OneDrive (or any cloud-sync) while running—file locks and sync conflicts will corrupt the CSV or TXT.
Avoid opening the MSI Afterburner CSV in Excel or another editor during monitoring. Always close it first.

Enjoy hassle-free, self-hosted temperature monitoring with real-time alerts and built-in analytics!
