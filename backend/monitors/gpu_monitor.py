import GPUtil
import wmi
import pythoncom

class GPUMonitor:
    def __init__(self):
        self.wmi = None
        # 초기화 시 WMI 시도해봄 (에러나면 무시)
        try:
            pythoncom.CoInitialize()
            self.wmi = wmi.WMI()
        except:
            pass

    def get_all(self) -> dict:
        gpus_info = []
        
        # 1. NVIDIA GPU 시도 (GPUtil)
        try:
            nvidia_gpus = GPUtil.getGPUs()
            for gpu in nvidia_gpus:
                gpus_info.append({
                    "id": gpu.id,
                    "name": gpu.name,
                    "load": gpu.load * 100,
                    "memory_total": gpu.memoryTotal,
                    "memory_used": gpu.memoryUsed,
                    "temperature": gpu.temperature
                })
        except Exception:
            pass

        # 2. NVIDIA를 못 찾았다면 WMI로 시도 (Intel/AMD)
        if not gpus_info:
            try:
                # 스레드별 COM 초기화 필요
                pythoncom.CoInitialize()
                w = wmi.WMI()
                
                for i, gpu in enumerate(w.Win32_VideoController()):
                    # 불필요한 어댑터 제외
                    if "Remote" in gpu.Name or "Virtual" in gpu.Name: continue
                    
                    # 메모리나 로드율 정보를 얻기 어려우므로 기본값 처리
                    try:
                        # AdapterRAM은 바이트 단위 -> MB 변환
                        mem_total = int(gpu.AdapterRAM) / (1024**2) if gpu.AdapterRAM else 0
                    except:
                        mem_total = 0
                        
                    gpus_info.append({
                        "id": i,
                        "name": gpu.Name,
                        "load": 0, # Load율 수집 불가 (0%)
                        "memory_total": mem_total,
                        "memory_used": 0,
                        "temperature": 0 # 온도 수집 불가
                    })
            except Exception as e:
                # WMI 에러 시 무시
                pass

        return {
            "available": len(gpus_info) > 0,
            "count": len(gpus_info),
            "gpus": gpus_info
        }
