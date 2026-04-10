import clr
import os
import sys

dll_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dll")
sys.path.append(dll_folder)
clr.AddReference(os.path.join(dll_folder, "LibreHardwareMonitorLib"))

from LibreHardwareMonitor.Hardware import Computer, SensorType  # type: ignore

class TempReader:
    def __init__(self):
        self.computer = Computer()
        self.computer.IsCpuEnabled = True
        self.computer.IsGpuEnabled = True
        self.computer.Open()

    def read(self) -> dict:
        temps = {"CPU": None, "GPU": None}
        for hardware in self.computer.Hardware:
            hardware.Update()
            for sub in hardware.SubHardware:
                sub.Update()
            for sensor in hardware.Sensors:
                if sensor.SensorType == SensorType.Temperature:
                    name = str(sensor.Name)
                    value = float(sensor.Value) if sensor.Value is not None else None
                    if "Tctl/Tdie" in name or "CPU" in name:
                        temps["CPU"] = value
                    elif "GPU Core" in name:
                        temps["GPU"] = value
        return temps

    def close(self):
        self.computer.Close()