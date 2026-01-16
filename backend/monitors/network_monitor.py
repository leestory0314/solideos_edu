import psutil
import time

class NetworkMonitor:
    """네트워크 트래픽 모니터링"""
    
    def __init__(self):
        self.last_io = None
        self.last_time = None
    
    def get_interfaces(self) -> dict:
        """네트워크 인터페이스 정보 반환"""
        interfaces = {}
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        for interface, addresses in addrs.items():
            if interface in stats:
                stat = stats[interface]
                interface_info = {
                    "is_up": stat.isup,
                    "speed": stat.speed,
                    "addresses": []
                }
                
                for addr in addresses:
                    interface_info["addresses"].append({
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask
                    })
                
                interfaces[interface] = interface_info
        
        return interfaces
    
    def get_io_counters(self) -> dict:
        """네트워크 I/O 카운터 반환"""
        io = psutil.net_io_counters()
        
        return {
            "bytes_sent": io.bytes_sent,
            "bytes_recv": io.bytes_recv,
            "packets_sent": io.packets_sent,
            "packets_recv": io.packets_recv,
            "errin": io.errin,
            "errout": io.errout,
            "dropin": io.dropin,
            "dropout": io.dropout,
            "bytes_sent_formatted": self._format_bytes(io.bytes_sent),
            "bytes_recv_formatted": self._format_bytes(io.bytes_recv)
        }
    
    def get_speed(self) -> dict:
        """현재 네트워크 속도 계산 (bytes/sec)"""
        current_io = psutil.net_io_counters()
        current_time = time.time()
        
        if self.last_io is None or self.last_time is None:
            self.last_io = current_io
            self.last_time = current_time
            return {
                "upload_speed": 0,
                "download_speed": 0,
                "upload_speed_formatted": "0 B/s",
                "download_speed_formatted": "0 B/s"
            }
        
        time_diff = current_time - self.last_time
        if time_diff == 0:
            time_diff = 1
        
        upload_speed = (current_io.bytes_sent - self.last_io.bytes_sent) / time_diff
        download_speed = (current_io.bytes_recv - self.last_io.bytes_recv) / time_diff
        
        self.last_io = current_io
        self.last_time = current_time
        
        return {
            "upload_speed": upload_speed,
            "download_speed": download_speed,
            "upload_speed_formatted": self._format_speed(upload_speed),
            "download_speed_formatted": self._format_speed(download_speed)
        }
    
    def _format_bytes(self, bytes_value: int) -> str:
        """바이트를 읽기 쉬운 형식으로 변환"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.2f} PB"
    
    def _format_speed(self, bytes_per_sec: float) -> str:
        """속도를 읽기 쉬운 형식으로 변환"""
        for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
            if bytes_per_sec < 1024:
                return f"{bytes_per_sec:.2f} {unit}"
            bytes_per_sec /= 1024
        return f"{bytes_per_sec:.2f} TB/s"
    
    def get_connections(self) -> dict:
        """네트워크 연결 정보 반환"""
        connections = psutil.net_connections(kind='inet')
        
        status_count = {}
        for conn in connections:
            status = conn.status
            status_count[status] = status_count.get(status, 0) + 1
        
        return {
            "total": len(connections),
            "by_status": status_count
        }
    
    def get_all(self) -> dict:
        """모든 네트워크 정보 반환"""
        return {
            "interfaces": self.get_interfaces(),
            "io": self.get_io_counters(),
            "speed": self.get_speed(),
            "connections": self.get_connections()
        }
