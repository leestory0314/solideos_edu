import psutil
import platform

class CPUMonitor:
    """CPU 사용량 및 온도 모니터링"""
    
    def __init__(self):
        self.temperature_available = False
        self._check_temperature_support()
    
    def _check_temperature_support(self):
        """온도 모니터링 지원 여부 확인"""
        try:
            if platform.system() == "Windows":
                import wmi
                self.wmi = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                self.temperature_available = True
            else:
                temps = psutil.sensors_temperatures()
                self.temperature_available = len(temps) > 0
        except Exception:
            self.temperature_available = False
    
    def get_usage(self) -> dict:
        """CPU 사용량 정보 반환"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count(logical=True)
        cpu_count_physical = psutil.cpu_count(logical=False)
        
        return {
            "percent": cpu_percent,
            "per_core": cpu_per_core,
            "frequency": {
                "current": cpu_freq.current if cpu_freq else 0,
                "min": cpu_freq.min if cpu_freq else 0,
                "max": cpu_freq.max if cpu_freq else 0
            },
            "cores": {
                "logical": cpu_count,
                "physical": cpu_count_physical
            }
        }
    
    def get_temperature(self) -> dict:
        """CPU 온도 정보 반환"""
        temperature = None
        
        try:
            if platform.system() == "Windows" and self.temperature_available:
                sensors = self.wmi.Sensor()
                for sensor in sensors:
                    if sensor.SensorType == "Temperature" and "CPU" in sensor.Name:
                        temperature = sensor.Value
                        break
            elif platform.system() != "Windows":
                temps = psutil.sensors_temperatures()
                if "coretemp" in temps:
                    temperature = temps["coretemp"][0].current
                elif temps:
                    first_key = list(temps.keys())[0]
                    temperature = temps[first_key][0].current
        except Exception:
            pass
        
        return {
            "available": temperature is not None,
            "value": temperature if temperature else 0,
            "unit": "°C"
        }
    
    def get_all(self) -> dict:
        """모든 CPU 정보 반환"""
        return {
            "usage": self.get_usage(),
            "temperature": self.get_temperature()
        }
