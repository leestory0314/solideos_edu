import psutil

class MemoryMonitor:
    """메모리 사용량 모니터링"""
    
    def get_virtual_memory(self) -> dict:
        """가상 메모리(RAM) 정보 반환"""
        mem = psutil.virtual_memory()
        
        return {
            "total": self._bytes_to_gb(mem.total),
            "available": self._bytes_to_gb(mem.available),
            "used": self._bytes_to_gb(mem.used),
            "free": self._bytes_to_gb(mem.free),
            "percent": mem.percent,
            "total_bytes": mem.total,
            "used_bytes": mem.used
        }
    
    def get_swap_memory(self) -> dict:
        """스왑 메모리 정보 반환"""
        swap = psutil.swap_memory()
        
        return {
            "total": self._bytes_to_gb(swap.total),
            "used": self._bytes_to_gb(swap.used),
            "free": self._bytes_to_gb(swap.free),
            "percent": swap.percent
        }
    
    def _bytes_to_gb(self, bytes_value: int) -> float:
        """바이트를 GB로 변환"""
        return round(bytes_value / (1024 ** 3), 2)
    
    def get_all(self) -> dict:
        """모든 메모리 정보 반환"""
        return {
            "virtual": self.get_virtual_memory(),
            "swap": self.get_swap_memory()
        }
