import psutil

class ProcessMonitor:
    """프로세스 모니터링 모듈"""
    
    def get_top_cpu(self, limit: int = 5) -> list:
        """CPU 사용률 상위 프로세스 반환"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                # cpu_percent 호출 시 interval=None이어야 blocking되지 않음
                # 최초 호출 시 0.0을 반환할 수 있으므로, 메인 루프에서 지속 호출 필요
                proc.cpu_percent(interval=None) 
                processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # 정렬 (내림차순)
        top_cpu = sorted(processes, key=lambda p: p.info['cpu_percent'], reverse=True)[:limit]
        
        return [
            {
                "pid": p.info['pid'],
                "name": p.info['name'],
                "value": p.info['cpu_percent']
            } 
            for p in top_cpu
        ]
        
    def get_top_memory(self, limit: int = 5) -> list:
        """메모리 사용률 상위 프로세스 반환"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        # 정렬 (내림차순)
        top_mem = sorted(processes, key=lambda p: p.info['memory_percent'], reverse=True)[:limit]
        
        return [
            {
                "pid": p.info['pid'],
                "name": p.info['name'],
                "value": round(p.info['memory_percent'], 1)
            } 
            for p in top_mem
        ]
        
    def get_top_network(self, limit: int = 5) -> list:
        """네트워크 연결 수 상위 프로세스 반환"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    # 연결 수 가져오기 (오버헤드 주의, 권한 에러 가능성 높음)
                    conns = len(proc.connections())
                    if conns > 0:
                        processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "value": conns
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, Exception):
                    continue
        except Exception:
            pass
        
        # 정렬 (내림차순)
        top_net = sorted(processes, key=lambda p: p['value'], reverse=True)[:limit]
        return top_net

    def get_top_disk(self, limit: int = 5) -> list:
        """디스크 I/O 상위 프로세스 반환"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    io = proc.io_counters()
                    if io:
                        # 읽기+쓰기 바이트 합계 (MB 단위 환산)
                        total_io = (io.read_bytes + io.write_bytes) / (1024 * 1024)
                        if total_io > 0:
                            processes.append({
                                "pid": proc.info['pid'],
                                "name": proc.info['name'],
                                "value": round(total_io, 2)
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, Exception):
                    continue
        except Exception:
            pass
        
        # 정렬 (내림차순)
        top_disk = sorted(processes, key=lambda p: p['value'], reverse=True)[:limit]
        return top_disk
        
    def get_all(self, limit: int = 5) -> dict:
        """모든 Top 프로세스 정보 반환"""
        return {
            "cpu_top": self.get_top_cpu(limit),
            "memory_top": self.get_top_memory(limit),
            "disk_top": self.get_top_disk(limit),
            "network_top": self.get_top_network(limit)
        }
