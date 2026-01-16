/**
 * Chart.js 실시간 차트 컴포넌트
 */

class ChartManager {
    constructor() {
        this.charts = {};
        this.maxDataPoints = 60; // 60초 데이터
        this.init();
    }

    init() {
        // Chart.js 기본 설정
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.color = '#94A3B8';
        Chart.defaults.plugins.legend.display = false;

        this.createCPUChart();
        this.createMemoryChart();
        this.createNetworkChart();
    }

    createCPUChart() {
        const ctx = document.getElementById('cpuChart');
        if (!ctx) return;

        this.charts.cpu = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU Usage',
                    data: [],
                    borderColor: '#60A5FA',
                    backgroundColor: 'rgba(96, 165, 250, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    pointHoverBackgroundColor: '#60A5FA'
                }]
            },
            options: this.getChartOptions('CPU Usage (%)', 100)
        });
    }

    createMemoryChart() {
        const ctx = document.getElementById('memoryChart');
        if (!ctx) return;

        this.charts.memory = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Memory Usage',
                    data: [],
                    borderColor: '#34D399',
                    backgroundColor: 'rgba(52, 211, 153, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    pointHoverBackgroundColor: '#34D399'
                }]
            },
            options: this.getChartOptions('Memory Usage (%)', 100)
        });
    }

    createNetworkChart() {
        const ctx = document.getElementById('networkChart');
        if (!ctx) return;

        this.charts.network = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Upload',
                        data: [],
                        borderColor: '#60A5FA',
                        backgroundColor: 'rgba(96, 165, 250, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0
                    },
                    {
                        label: 'Download',
                        data: [],
                        borderColor: '#34D399',
                        backgroundColor: 'rgba(52, 211, 153, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0
                    }
                ]
            },
            options: this.getChartOptions('Speed (KB/s)', null)
        });
    }

    getChartOptions(yAxisTitle, suggestedMax) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            animation: {
                duration: 750,
                easing: 'linear'
            },
            scales: {
                x: {
                    display: true,
                    grid: {
                        display: false, // 그리드 최소화
                        color: 'rgba(148, 163, 184, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: 'rgba(148, 163, 184, 0.5)',
                        maxTicksLimit: 10,
                        font: { size: 10 },
                        maxRotation: 0
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: false, // 타이틀 제거하여 공간 확보
                    },
                    min: 0,
                    suggestedMax: suggestedMax,
                    grid: {
                        color: 'rgba(148, 163, 184, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: 'rgba(148, 163, 184, 0.5)',
                        font: { size: 10 }
                    }
                }
            },
            plugins: {
                tooltip: {
                    enabled: true,
                    intersect: false,
                    mode: 'index',
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#F1F5F9',
                    bodyColor: '#CBD5E1',
                    borderColor: 'rgba(148, 163, 184, 0.2)',
                    borderWidth: 1,
                    padding: 10,
                    cornerRadius: 6,
                    displayColors: true,
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y.toFixed(1);
                                if (context.chart.options.scales.y.suggestedMax === 100) {
                                    label += '%';
                                } else if (!context.chart.options.scales.y.suggestedMax) {
                                    label += ' KB/s';
                                }
                            }
                            return label;
                        }
                    }
                }
            }
        };
    }

    updateChart(chartName, value, label) {
        const chart = this.charts[chartName];
        if (!chart) return;

        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(value);

        // 최대 데이터 포인트 유지
        if (chart.data.labels.length > this.maxDataPoints) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.update(); // 애니메이션 적용
    }

    updateNetworkChart(uploadSpeed, downloadSpeed, label) {
        const chart = this.charts.network;
        if (!chart) return;

        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(uploadSpeed);
        chart.data.datasets[1].data.push(downloadSpeed);

        // 최대 데이터 포인트 유지
        if (chart.data.labels.length > this.maxDataPoints) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
            chart.data.datasets[1].data.shift();
        }

        chart.update(); // 애니메이션 적용
    }

    resetAllCharts() {
        Object.values(this.charts).forEach(chart => {
            chart.data.labels = [];
            chart.data.datasets.forEach(dataset => {
                dataset.data = [];
            });
            chart.update('none');
        });
    }
}

// 전역 인스턴스
window.chartManager = new ChartManager();
