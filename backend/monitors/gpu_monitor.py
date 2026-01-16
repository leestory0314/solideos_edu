import platform

class GPUMonitor:
    """GPU 사용량 및 온도 모니터링"""
    
    def __init__(self):
        self.gpu_available = False
        self.gpu_type = None
        self._check_gpu_support()
    
    def _check_gpu_support(self):
        """GPU 모니터링 지원 여부 확인"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                self.gpu_available = True
                self.gpu_type = "NVIDIA"
        except Exception:
            pass
        
        if not self.gpu_available:
            try:
                if platform.system() == "Windows":
                    import wmi
                    self.wmi = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                    sensors = self.wmi.Sensor()
                    for sensor in sensors:
                        if "GPU" in sensor.Name:
                            self.gpu_available = True
                            self.gpu_type = "OpenHardwareMonitor"
                            break
            except Exception:
                pass
    
    def get_nvidia_info(self) -> list:
        """NVIDIA GPU 정보 반환"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            gpu_list = []
            
            for gpu in gpus:
                gpu_list.append({
                    "id": gpu.id,
                    "name": gpu.name,
                    "load": gpu.load * 100,
                    "memory": {
                        "total": gpu.memoryTotal,
                        "used": gpu.memoryUsed,
                        "free": gpu.memoryFree,
                        "percent": (gpu.memoryUsed / gpu.memoryTotal * 100) if gpu.memoryTotal > 0 else 0
                    },
                    "temperature": gpu.temperature,
                    "driver": gpu.driver
                })
            
            return gpu_list
        except Exception:
            return []
    
    def get_ohm_info(self) -> list:
        """OpenHardwareMonitor를 통한 GPU 정보 반환"""
        try:
            if not hasattr(self, 'wmi'):
                import wmi
                self.wmi = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            
            sensors = self.wmi.Sensor()
            gpu_data = {
                "id": 0,
                "name": "GPU",
                "load": 0,
                "memory": {"total": 0, "used": 0, "free": 0, "percent": 0},
                "temperature": 0,
                "driver": "N/A"
            }
            
            for sensor in sensors:
                if "GPU" in sensor.Name:
                    if sensor.SensorType == "Load" and "Core" in sensor.Name:
                        gpu_data["load"] = sensor.Value
                    elif sensor.SensorType == "Temperature":
                        gpu_data["temperature"] = sensor.Value
                    elif sensor.SensorType == "SmallData" and "Memory" in sensor.Name:
                        if "Used" in sensor.Name:
                            gpu_data["memory"]["used"] = sensor.Value
                        elif "Total" in sensor.Name:
                            gpu_data["memory"]["total"] = sensor.Value
            
            if gpu_data["memory"]["total"] > 0:
                gpu_data["memory"]["percent"] = (gpu_data["memory"]["used"] / gpu_data["memory"]["total"]) * 100
                gpu_data["memory"]["free"] = gpu_data["memory"]["total"] - gpu_data["memory"]["used"]
            
            return [gpu_data]
        except Exception:
            return []
    
    def get_all(self) -> dict:
        """모든 GPU 정보 반환"""
        gpus = []
        
        if self.gpu_available:
            if self.gpu_type == "NVIDIA":
                gpus = self.get_nvidia_info()
            elif self.gpu_type == "OpenHardwareMonitor":
                gpus = self.get_ohm_info()
        
        return {
            "available": self.gpu_available,
            "type": self.gpu_type,
            "gpus": gpus
        }
