import psutil

class DiskMonitor:
    """디스크 사용량 모니터링"""
    
    def get_partitions(self) -> list:
        """모든 디스크 파티션 정보 반환"""
        partitions = []
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": self._bytes_to_gb(usage.total),
                    "used": self._bytes_to_gb(usage.used),
                    "free": self._bytes_to_gb(usage.free),
                    "percent": usage.percent
                })
            except PermissionError:
                continue
            except Exception:
                continue
        
        return partitions
    
    def get_io_counters(self) -> dict:
        """디스크 I/O 카운터 반환"""
        io = psutil.disk_io_counters()
        
        if io:
            return {
                "read_count": io.read_count,
                "write_count": io.write_count,
                "read_bytes": self._bytes_to_mb(io.read_bytes),
                "write_bytes": self._bytes_to_mb(io.write_bytes),
                "read_time": io.read_time,
                "write_time": io.write_time
            }
        return {}
    
    def _bytes_to_gb(self, bytes_value: int) -> float:
        """바이트를 GB로 변환"""
        return round(bytes_value / (1024 ** 3), 2)
    
    def _bytes_to_mb(self, bytes_value: int) -> float:
        """바이트를 MB로 변환"""
        return round(bytes_value / (1024 ** 2), 2)
    
    def get_all(self) -> dict:
        """모든 디스크 정보 반환"""
        return {
            "partitions": self.get_partitions(),
            "io": self.get_io_counters()
        }
