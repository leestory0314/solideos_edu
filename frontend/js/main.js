/**
 * Main Application Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    initApp();
});

function initApp() {
    wsManager.onConnectionChange(handleConnectionChange);
    wsManager.onData(handleData);
    wsManager.connect();
    setupEventListeners();
}

function setupEventListeners() {
    document.getElementById('startMonitoringBtn').addEventListener('click', startMonitoring);
    document.getElementById('stopMonitoringBtn').addEventListener('click', stopMonitoring);
    document.getElementById('reportsBtn').addEventListener('click', () => toggleModal('reportsModal', true));
    document.getElementById('closeReportsBtn').addEventListener('click', () => toggleModal('reportsModal', false));
    document.querySelector('.modal-overlay').addEventListener('click', () => toggleModal('reportsModal', false));
}

function handleConnectionChange(connected) {
    const statusEl = document.getElementById('connectionStatus');
    const textEl = statusEl.querySelector('.status-text');
    statusEl.className = 'connection-status ' + (connected ? 'connected' : 'disconnected');
    textEl.textContent = connected ? 'Connected' : 'Disconnected';
}

function handleData(data) {
    updateCPU(data.cpu);
    updateGPU(data.gpu);
    updateMemory(data.memory);
    updateNetwork(data.network);
    updateDisk(data.disk);
    updateProcesses(data.processes);
    updateCharts(data);
    if (data.monitoring) updateMonitoringStatus(data.monitoring);
    if (data.monitoring_complete) handleMonitoringComplete(data);
}

function updateCPU(cpu) {
    if (!cpu) return;
    const usage = cpu.usage.percent;
    document.getElementById('cpuUsage').textContent = usage.toFixed(0);
    document.getElementById('cpuCores').textContent = `${cpu.usage.cores.logical} cores`;
    document.getElementById('cpuFreq').textContent = cpu.usage.frequency.current.toFixed(0);
    document.getElementById('cpuTemp').textContent = cpu.temperature.available ? cpu.temperature.value.toFixed(0) : '--';
    updateRing('cpuRing', usage);
    updateCardStatus('cpuCard', 'cpuStatus', usage, 60, 85);
}

function updateGPU(gpu) {
    if (!gpu) return;
    if (gpu.available && gpu.gpus.length > 0) {
        const g = gpu.gpus[0];
        document.getElementById('gpuUsage').textContent = g.load.toFixed(0);
        document.getElementById('gpuName').textContent = g.name.substring(0, 20);
        document.getElementById('gpuTemp').textContent = g.temperature.toFixed(0);
        document.getElementById('gpuMemory').textContent = g.memory.used.toFixed(0);
        updateRing('gpuRing', g.load);
        updateCardStatus('gpuCard', 'gpuStatus', g.load, 70, 90);
    } else {
        document.getElementById('gpuName').textContent = 'N/A';
    }
}

function updateMemory(mem) {
    if (!mem) return;
    const v = mem.virtual;
    document.getElementById('memoryUsage').textContent = v.percent.toFixed(0);
    document.getElementById('memoryTotal').textContent = `${v.total} GB Total`;
    document.getElementById('memoryUsed').textContent = v.used.toFixed(1);
    document.getElementById('memoryFree').textContent = v.available.toFixed(1);
    updateRing('memoryRing', v.percent);
    updateCardStatus('memoryCard', 'memoryStatus', v.percent, 70, 90);
}

function updateNetwork(net) {
    if (!net) return;
    document.getElementById('uploadSpeed').textContent = net.speed.upload_speed_formatted;
    document.getElementById('downloadSpeed').textContent = net.speed.download_speed_formatted;
    document.getElementById('totalSent').textContent = net.io.bytes_sent_formatted;
    document.getElementById('totalReceived').textContent = net.io.bytes_recv_formatted;
    document.getElementById('networkConnections').textContent = `${net.connections.total} connections`;
}

function updateDisk(disk) {
    if (!disk) return;
    const grid = document.getElementById('diskGrid');
    grid.innerHTML = disk.partitions.map(p => {
        const status = p.percent >= 90 ? 'danger' : (p.percent >= 80 ? 'warning' : 'normal');
        return `<div class="disk-card">
            <div class="disk-header">
                <div class="disk-name"><i data-lucide="hard-drive"></i>${p.mountpoint}</div>
                <span class="disk-percent ${status}">${p.percent.toFixed(0)}%</span>
            </div>
            <div class="disk-bar"><div class="disk-bar-fill ${status}" style="width:${p.percent}%"></div></div>
            <div class="disk-info"><span>${p.used} GB used</span><span>${p.free} GB free</span></div>
        </div>`;
    }).join('');
    lucide.createIcons();
}

let dataCounter = 0;
function updateCharts(data) {
    dataCounter++;
    const label = `${dataCounter}s`;
    if (data.cpu) chartManager.updateChart('cpu', data.cpu.usage.percent, label);
    if (data.memory) chartManager.updateChart('memory', data.memory.virtual.percent, label);
    if (data.network) {
        const up = data.network.speed.upload_speed / 1024;
        const down = data.network.speed.download_speed / 1024;
        chartManager.updateNetworkChart(up, down, label);
    }
}

function updateRing(id, percent) {
    const ring = document.getElementById(id);
    if (!ring) return;
    const offset = 251.2 - (251.2 * percent / 100);
    ring.style.strokeDashoffset = offset;
    ring.className.baseVal = 'progress-ring-fill ' + (percent >= 85 ? 'danger' : (percent >= 60 ? 'warning' : ''));
}

function updateCardStatus(cardId, statusId, value, warnThresh, dangerThresh) {
    const card = document.getElementById(cardId);
    const status = document.getElementById(statusId);
    const badge = status.querySelector('.status-badge');
    card.classList.remove('warning', 'danger');
    if (value >= dangerThresh) {
        card.classList.add('danger');
        badge.className = 'status-badge danger';
        badge.textContent = 'Critical';
    } else if (value >= warnThresh) {
        card.classList.add('warning');
        badge.className = 'status-badge warning';
        badge.textContent = 'Warning';
    } else {
        badge.className = 'status-badge normal';
        badge.textContent = 'Normal';
    }
}

async function startMonitoring() {
    try {
        const res = await fetch('/api/start-monitoring', { method: 'POST' });
        if (res.ok) {
            document.getElementById('monitoringBar').classList.add('active');
            document.getElementById('startMonitoringBtn').disabled = true;
            showToast('5분 모니터링이 시작되었습니다.', 'info');
        } else {
            showToast('모니터링 시작 실패', 'error');
        }
    } catch (e) { showToast('오류: ' + e.message, 'error'); }
}

async function stopMonitoring() {
    try {
        const res = await fetch('/api/stop-monitoring', { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
            document.getElementById('monitoringBar').classList.remove('active');
            document.getElementById('startMonitoringBtn').disabled = false;
            showToast(`PDF 리포트가 생성되었습니다: ${data.pdf_path}`, 'success');
        }
    } catch (e) { showToast('오류: ' + e.message, 'error'); }
}

function updateMonitoringStatus(m) {
    const bar = document.getElementById('progressBar');
    const timer = document.getElementById('timerDisplay');
    const progress = (m.elapsed_seconds / 300) * 100;
    bar.style.width = `${progress}%`;
    const mins = Math.floor(m.remaining_seconds / 60);
    const secs = Math.floor(m.remaining_seconds % 60);
    timer.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    if (!m.active && document.getElementById('monitoringBar').classList.contains('active')) {
        document.getElementById('monitoringBar').classList.remove('active');
        document.getElementById('startMonitoringBtn').disabled = false;
    }
}

function handleMonitoringComplete(data) {
    showToast(`모니터링 완료! PDF: ${data.pdf_path || '생성됨'}`, 'success');
    loadReports();
}

async function loadReports() {
    try {
        const res = await fetch('/api/reports');
        const data = await res.json();
        const list = document.getElementById('reportsList');
        if (data.reports.length === 0) {
            list.innerHTML = '<div class="no-reports"><i data-lucide="file-x"></i><p>No reports yet</p></div>';
        } else {
            list.innerHTML = data.reports.map(r => `
                <div class="report-item">
                    <div class="report-info">
                        <span class="report-name">${r.filename}</span>
                        <div class="report-meta">
                            <span>${(r.size / 1024).toFixed(1)} KB</span>
                            <span>${new Date(r.created).toLocaleString()}</span>
                        </div>
                    </div>
                    <div class="report-actions">
                        <a href="/api/download-report/${r.filename}" class="btn btn-primary btn-sm" download>
                            <i data-lucide="download"></i>
                        </a>
                    </div>
                </div>
            `).join('');
        }
        lucide.createIcons();
    } catch (e) { console.error(e); }
}

function toggleModal(id, show) {
    const modal = document.getElementById(id);
    if (show) { modal.classList.add('active'); loadReports(); }
    else modal.classList.remove('active');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const icons = { success: 'check-circle', error: 'x-circle', info: 'info' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<i data-lucide="${icons[type]}" class="toast-icon"></i>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()"><i data-lucide="x"></i></button>`;
    container.appendChild(toast);
    lucide.createIcons();
    setTimeout(() => toast.remove(), 5000);
}

function updateProcesses(processes) {
    if (!processes) return;

    // Helper to create table rows
    const createRows = (list, valueFormatter, thresh1, thresh2) => {
        return list.map(p => {
            const usageClass = p.value >= thresh2 ? 'critical-usage' : (p.value >= thresh1 ? 'high-usage' : '');
            return `
                <tr>
                    <td><span class="process-name" title="${p.name}">${p.name}</span></td>
                    <td class="text-muted">${p.pid}</td>
                    <td class="text-right ${usageClass}">${valueFormatter(p.value)}</td>
                </tr>
            `;
        }).join('');
    };

    // Update CPU Top 5
    const cpuTable = document.querySelector('#cpuProcessTable tbody');
    if (cpuTable && processes.cpu_top) {
        cpuTable.innerHTML = createRows(processes.cpu_top, val => `${val.toFixed(1)}%`, 10, 20);
    }

    // Update Memory Top 5
    const memTable = document.querySelector('#memoryProcessTable tbody');
    if (memTable && processes.memory_top) {
        memTable.innerHTML = createRows(processes.memory_top, val => `${val.toFixed(1)}%`, 10, 20);
    }

    // Update Network Top 5
    const netTable = document.querySelector('#networkProcessTable tbody');
    if (netTable && processes.network_top) {
        netTable.innerHTML = createRows(processes.network_top, val => `${val}`, 10, 50);
    }

    // Update Disk Top 5
    const diskTable = document.querySelector('#diskProcessTable tbody');
    if (diskTable && processes.disk_top) {
        diskTable.innerHTML = createRows(processes.disk_top, val => `${val.toFixed(2)} MB`, 50, 100);
    }
}
