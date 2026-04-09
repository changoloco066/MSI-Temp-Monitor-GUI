import clr
import os
import sys
import time

dll_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dll")
sys.path.append(dll_folder)
clr.AddReference(os.path.join(dll_folder, "LibreHardwareMonitorLib"))

from LibreHardwareMonitor.Hardware import Computer  # type: ignore

c = Computer()
c.IsCpuEnabled = True
c.IsGpuEnabled = True
c.Open()

while True:
    for a in range(0, len(c.Hardware[0].Sensors)):
        if "/temperature" in str(c.Hardware[0].Sensors[a].Identifier):
            print(c.Hardware[0].Sensors[a].Value)
            c.Hardware[0].Update()
            time.sleep(1)