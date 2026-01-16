# 시스템 리소스 실시간 모니터링 시스템

## 📋 소프트웨어 사양서 (Specification)

### 1. 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | System Resource Monitor |
| **버전** | 1.0.0 |
| **플랫폼** | Windows (Linux/Mac 부분 지원) |
| **아키텍처** | Client-Server (WebSocket 기반 실시간 통신) |

### 2. 주요 기능

#### 2.1 실시간 모니터링
- **CPU**: 사용량(%), 코어별 사용량, 주파수, 온도
- **GPU**: 사용량(%), VRAM 사용량, 온도 (NVIDIA 지원)
- **Memory**: 총 용량, 사용량, 가용량, 사용률(%)
- **Disk**: 파티션별 사용량, I/O 카운터
- **Network**: 업로드/다운로드 속도, 총 전송량, 연결 수

#### 2.2 시각화
- 실시간 라인 차트 (CPU, Memory, Network)
- 원형 프로그레스 링 (각 리소스 카드)
- 바 차트 (디스크 사용량)

#### 2.3 5분 모니터링 & PDF 리포트
- 5분간 1초 단위 데이터 수집
- 자동 PDF 리포트 생성
- 요약 통계, 그래프, 시스템 정보 포함

### 3. 기술 스택

```
Backend (Python 3.8+)
├── FastAPI 0.109.0      - REST API 프레임워크
├── uvicorn 0.27.0       - ASGI 서버
├── websockets 12.0      - 실시간 통신
├── psutil 5.9.8         - 시스템 정보 수집
├── GPUtil 1.4.0         - NVIDIA GPU 모니터링
├── WMI 1.5.1            - Windows 하드웨어 정보
├── reportlab 4.0.8      - PDF 생성
└── matplotlib 3.8.2     - 차트 생성

Frontend (Vanilla JS)
├── HTML5 / CSS3
├── Chart.js             - 동적 차트
└── Lucide Icons         - 모던 아이콘
```

### 4. 디자인 시스템

#### 4.1 컬러 팔레트

| 상태 | Primary | Secondary | Background |
|------|---------|-----------|------------|
| 정상 (Normal) | `#3B82F6` | `#60A5FA` | `#EFF6FF` |
| 경고 (Warning) | `#F59E0B` | `#FBBF24` | `#FFFBEB` |
| 위험 (Danger) | `#EF4444` | `#F87171` | `#FEF2F2` |

#### 4.2 상태 임계값

| 리소스 | 정상 | 경고 | 위험 |
|--------|------|------|------|
| CPU 사용량 | 0-60% | 60-85% | 85%+ |
| CPU 온도 | 0-60°C | 60-80°C | 80°C+ |
| GPU 사용량 | 0-70% | 70-90% | 90%+ |
| GPU 온도 | 0-70°C | 70-85°C | 85°C+ |
| Memory | 0-70% | 70-90% | 90%+ |
| Disk | 0-80% | 80-90% | 90%+ |

### 5. API 명세

#### REST Endpoints

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/` | 메인 대시보드 |
| GET | `/api/status` | 현재 시스템 상태 |
| GET | `/api/system-info` | 시스템 정보 |
| POST | `/api/start-monitoring` | 5분 모니터링 시작 |
| POST | `/api/stop-monitoring` | 모니터링 중지 & PDF 생성 |
| GET | `/api/monitoring-status` | 모니터링 상태 확인 |
| GET | `/api/reports` | 생성된 리포트 목록 |
| GET | `/api/download-report/{filename}` | PDF 다운로드 |

#### WebSocket

- **Endpoint**: `ws://localhost:8000/ws`
- **Data**: 1초마다 전체 시스템 데이터 전송 (JSON)

### 6. 프로젝트 구조

```
2nd_antigravity/
├── backend/
│   ├── main.py                 # FastAPI 서버
│   ├── pdf_generator.py        # PDF 생성 모듈
│   ├── requirements.txt        # Python 의존성
│   └── monitors/
│       ├── __init__.py
│       ├── cpu_monitor.py      # CPU 모니터링
│       ├── gpu_monitor.py      # GPU 모니터링
│       ├── memory_monitor.py   # 메모리 모니터링
│       ├── disk_monitor.py     # 디스크 모니터링
│       └── network_monitor.py  # 네트워크 모니터링
├── frontend/
│   ├── index.html              # 메인 대시보드
│   ├── css/
│   │   └── style.css           # 스타일시트
│   └── js/
│       ├── main.js             # 메인 로직
│       ├── charts.js           # 차트 컴포넌트
│       └── websocket.js        # WebSocket 클라이언트
└── reports/                    # 생성된 PDF 저장
```

### 7. 실행 방법

#### 7.1 환경 설정
```powershell
# Python 3.8+ 설치 필요
# 의존성 설치
cd backend
pip install -r requirements.txt
```

#### 7.2 서버 실행
```powershell
cd backend
python main.py
```

#### 7.3 접속
- 브라우저에서 `http://localhost:8000` 접속

### 8. PDF 리포트 구성

1. **헤더**: 리포트 제목, 생성 시간, 모니터링 기간
2. **요약 테이블**: 각 리소스별 Min/Max/Average/Status
3. **CPU 그래프**: 시간별 CPU 사용량 라인 차트
4. **Memory 그래프**: 시간별 메모리 사용량 라인 차트
5. **Network 그래프**: 업로드/다운로드 속도 이중 라인 차트
6. **Disk 바 차트**: 파티션별 사용량
7. **시스템 정보 테이블**: OS, CPU, RAM 등 상세 정보

### 9. 주의사항

⚠️ **GPU 온도 모니터링**
- NVIDIA GPU: GPUtil 라이브러리 사용 (자동)
- AMD GPU: 별도 드라이버/라이브러리 필요

⚠️ **CPU 온도 모니터링**
- Windows: OpenHardwareMonitor 또는 LibreHardwareMonitor 실행 필요
- 관리자 권한 필요할 수 있음

---

**작성일**: 2026-01-16
**버전**: 1.0.0
