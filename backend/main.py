import asyncio
import json
import os
import platform
from datetime import datetime
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from monitors import CPUMonitor, GPUMonitor, MemoryMonitor, DiskMonitor, NetworkMonitor, ProcessMonitor
from pdf_generator import PDFGenerator

# 모니터 인스턴스
cpu_monitor = CPUMonitor()
gpu_monitor = GPUMonitor()
memory_monitor = MemoryMonitor()
disk_monitor = DiskMonitor()
network_monitor = NetworkMonitor()
process_monitor = ProcessMonitor()
pdf_generator = PDFGenerator(output_dir="../reports")

# 모니터링 데이터 저장소
monitoring_data: Dict[str, List] = {
    "cpu": [],
    "memory": [],
    "gpu": [],
    "cpu_temp": [],
    "gpu_temp": [],
    "network_upload": [],
    "network_download": [],
    "disk": [],
    "timestamps": []
}

# 모니터링 상태
monitoring_active = False
monitoring_start_time = None

# 프로세스 CPU 퍼센트 초기화를 위한 더미 호출
import psutil
for p in psutil.process_iter(['cpu_percent']):
    try:
        p.cpu_percent()
    except:
        pass

# WebSocket 연결 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[*] System Resource Monitor Server Starting...")
    print(f"[*] Platform: {platform.system()} {platform.release()}")
    print(f"[*] Open http://localhost:8000 in your browser")
    yield
    # Shutdown
    print("[*] Server shutting down...")

app = FastAPI(
    title="System Resource Monitor",
    description="Real-time system resource monitoring with PDF report generation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static 파일 서빙
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

def get_system_data() -> dict:
    """모든 시스템 데이터 수집"""
    cpu_data = cpu_monitor.get_all()
    gpu_data = gpu_monitor.get_all()
    memory_data = memory_monitor.get_all()
    disk_data = disk_monitor.get_all()
    network_data = network_monitor.get_all()
    process_data = process_monitor.get_all(limit=5)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": cpu_data,
        "gpu": gpu_data,
        "memory": memory_data,
        "disk": disk_data,
        "network": network_data,
        "processes": process_data
    }

def get_system_info() -> dict:
    """시스템 정보 반환"""
    import psutil
    
    return {
        "Platform": platform.system(),
        "Platform Version": platform.version(),
        "Architecture": platform.machine(),
        "Processor": platform.processor(),
        "CPU Cores (Physical)": psutil.cpu_count(logical=False),
        "CPU Cores (Logical)": psutil.cpu_count(logical=True),
        "Total RAM": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
        "Python Version": platform.python_version()
    }

@app.get("/")
async def root():
    """메인 페이지"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "System Resource Monitor API", "docs": "/docs"}

@app.get("/api/status")
async def get_status():
    """현재 시스템 상태 반환"""
    return get_system_data()

@app.get("/api/system-info")
async def get_sys_info():
    """시스템 정보 반환"""
    return get_system_info()

@app.post("/api/start-monitoring")
async def start_monitoring():
    """5분 모니터링 시작"""
    global monitoring_active, monitoring_start_time, monitoring_data
    
    if monitoring_active:
        return JSONResponse(
            status_code=400,
            content={"error": "Monitoring already in progress"}
        )
    
    # 데이터 초기화
    monitoring_data = {
        "cpu": [],
        "memory": [],
        "gpu": [],
        "cpu_temp": [],
        "gpu_temp": [],
        "network_upload": [],
        "network_download": [],
        "disk": [],
        "timestamps": []
    }
    
    monitoring_active = True
    monitoring_start_time = datetime.now()
    
    return {"status": "monitoring_started", "start_time": monitoring_start_time.isoformat()}

@app.post("/api/stop-monitoring")
async def stop_monitoring():
    """모니터링 중지 및 PDF 생성"""
    global monitoring_active, monitoring_data
    
    if not monitoring_active:
        return JSONResponse(
            status_code=400,
            content={"error": "No monitoring in progress"}
        )
    
    monitoring_active = False
    
    # 디스크 정보 추가
    disk_data = disk_monitor.get_partitions()
    monitoring_data["disk"] = disk_data
    
    # 시스템 정보 추가
    monitoring_data["system_info"] = get_system_info()
    
    # PDF 생성
    try:
        pdf_path = pdf_generator.generate(monitoring_data, duration_minutes=5)
        return {
            "status": "monitoring_stopped",
            "pdf_path": pdf_path,
            "data_points": len(monitoring_data["cpu"])
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate PDF: {str(e)}"}
        )

@app.get("/api/monitoring-status")
async def get_monitoring_status():
    """모니터링 상태 확인"""
    global monitoring_active, monitoring_start_time
    
    elapsed = 0
    remaining = 300
    
    if monitoring_active and monitoring_start_time:
        elapsed = (datetime.now() - monitoring_start_time).total_seconds()
        remaining = max(0, 300 - elapsed)
    
    return {
        "active": monitoring_active,
        "elapsed_seconds": elapsed,
        "remaining_seconds": remaining,
        "data_points": len(monitoring_data["cpu"])
    }

@app.get("/api/download-report/{filename}")
async def download_report(filename: str):
    """PDF 리포트 다운로드"""
    # 파일명 검증 (경로 탐색 방지)
    if ".." in filename or "/" in filename or "\\" in filename:
         raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = os.path.join(REPORTS_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=filename
        )
    raise HTTPException(status_code=404, detail="Report not found")

@app.get("/api/reports")
async def list_reports():
    """생성된 리포트 목록"""
    if not os.path.exists(REPORTS_DIR):
        return {"reports": []}
    
    reports = []
    for filename in os.listdir(REPORTS_DIR):
        if filename.endswith(".pdf"):
            filepath = os.path.join(REPORTS_DIR, filename)
            try:
                created_time = os.path.getctime(filepath)
                reports.append({
                    "filename": filename,
                    "size": os.path.getsize(filepath),
                    "created": datetime.fromtimestamp(created_time).isoformat()
                })
            except OSError:
                continue
    
    return {"reports": sorted(reports, key=lambda x: x["created"], reverse=True)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """실시간 데이터 WebSocket 엔드포인트"""
    global monitoring_active, monitoring_data, monitoring_start_time
    
    await manager.connect(websocket)
    
    try:
        while True:
            # 시스템 데이터 수집
            data = get_system_data()
            
            # 모니터링 상태 추가
            elapsed = 0
            remaining = 300
            
            if monitoring_active and monitoring_start_time:
                elapsed = (datetime.now() - monitoring_start_time).total_seconds()
                remaining = max(0, 300 - elapsed)
                
                # 데이터 저장
                monitoring_data["cpu"].append(data["cpu"]["usage"]["percent"])
                monitoring_data["memory"].append(data["memory"]["virtual"]["percent"])
                monitoring_data["timestamps"].append(data["timestamp"])
                
                if data["cpu"]["temperature"]["available"]:
                    monitoring_data["cpu_temp"].append(data["cpu"]["temperature"]["value"])
                
                if data["gpu"]["available"] and data["gpu"]["gpus"]:
                    monitoring_data["gpu"].append(data["gpu"]["gpus"][0]["load"])
                    monitoring_data["gpu_temp"].append(data["gpu"]["gpus"][0]["temperature"])
                
                network_speed = data["network"]["speed"]
                monitoring_data["network_upload"].append(network_speed["upload_speed"] / 1024)
                monitoring_data["network_download"].append(network_speed["download_speed"] / 1024)
                
                # 5분 경과 시 자동 중지
                if elapsed >= 300:
                    monitoring_active = False
                    
                    # PDF 생성
                    disk_data = disk_monitor.get_partitions()
                    monitoring_data["disk"] = disk_data
                    monitoring_data["system_info"] = get_system_info()
                    
                    try:
                        pdf_path = pdf_generator.generate(monitoring_data, duration_minutes=5)
                        data["monitoring_complete"] = True
                        data["pdf_path"] = pdf_path
                    except Exception as e:
                        data["monitoring_complete"] = True
                        data["pdf_error"] = str(e)
            
            data["monitoring"] = {
                "active": monitoring_active,
                "elapsed_seconds": elapsed,
                "remaining_seconds": remaining,
                "data_points": len(monitoring_data["cpu"])
            }
            
            # 데이터 전송
            await websocket.send_json(data)
            
            # 1초 대기
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
