import os
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import numpy as np

class PDFGenerator:
    """PDF 리포트 생성기"""
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
             base_dir = os.path.dirname(os.path.abspath(__file__))
             self.output_dir = os.path.join(base_dir, "..", "reports")
        else:
            self.output_dir = output_dir
            
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 컬러 팔레트
        self.colors = {
            'primary': '#3B82F6',
            'secondary': '#60A5FA',
            'success': '#10B981',
            'warning': '#F59E0B',
            'danger': '#EF4444',
            'dark': '#1F2937',
            'light': '#F3F4F6'
        }
        
        # 스타일 설정
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1F2937')
        ))
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#3B82F6')
        ))
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            textColor=colors.HexColor('#374151')
        ))
    
    def _create_line_chart(self, data: list, title: str, ylabel: str, 
                           color: str = '#3B82F6', figsize=(8, 3)) -> io.BytesIO:
        """라인 차트 생성"""
        fig, ax = plt.subplots(figsize=figsize)
        
        x = list(range(len(data)))
        ax.plot(x, data, color=color, linewidth=2, marker='o', markersize=3)
        ax.fill_between(x, data, alpha=0.3, color=color)
        
        ax.set_title(title, fontsize=12, fontweight='bold', color='#1F2937')
        ax.set_ylabel(ylabel, fontsize=10, color='#6B7280')
        ax.set_xlabel('Time (seconds)', fontsize=10, color='#6B7280')
        
        ax.set_facecolor('#F9FAFB')
        fig.patch.set_facecolor('white')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Y축 범위 설정
        if max(data) <= 100:
            ax.set_ylim(0, 100)
        
        plt.tight_layout()
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        img_buffer.seek(0)
        
        return img_buffer
    
    def _create_dual_line_chart(self, data1: list, data2: list, 
                                 label1: str, label2: str,
                                 title: str, ylabel: str,
                                 color1: str = '#3B82F6', 
                                 color2: str = '#10B981',
                                 figsize=(8, 3)) -> io.BytesIO:
        """이중 라인 차트 생성"""
        fig, ax = plt.subplots(figsize=figsize)
        
        x = list(range(len(data1)))
        ax.plot(x, data1, color=color1, linewidth=2, label=label1, marker='o', markersize=2)
        ax.plot(x, data2, color=color2, linewidth=2, label=label2, marker='s', markersize=2)
        
        ax.set_title(title, fontsize=12, fontweight='bold', color='#1F2937')
        ax.set_ylabel(ylabel, fontsize=10, color='#6B7280')
        ax.set_xlabel('Time (seconds)', fontsize=10, color='#6B7280')
        
        ax.set_facecolor('#F9FAFB')
        fig.patch.set_facecolor('white')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(loc='upper right')
        
        plt.tight_layout()
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        img_buffer.seek(0)
        
        return img_buffer
    
    def _create_bar_chart(self, labels: list, values: list, 
                          title: str, ylabel: str,
                          figsize=(8, 3)) -> io.BytesIO:
        """바 차트 생성"""
        fig, ax = plt.subplots(figsize=figsize)
        
        # 값에 따른 색상 결정
        bar_colors = []
        for v in values:
            if v >= 90:
                bar_colors.append('#EF4444')  # 위험
            elif v >= 70:
                bar_colors.append('#F59E0B')  # 경고
            else:
                bar_colors.append('#3B82F6')  # 정상
        
        bars = ax.bar(labels, values, color=bar_colors, edgecolor='white', linewidth=1.5)
        
        ax.set_title(title, fontsize=12, fontweight='bold', color='#1F2937')
        ax.set_ylabel(ylabel, fontsize=10, color='#6B7280')
        
        ax.set_facecolor('#F9FAFB')
        fig.patch.set_facecolor('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylim(0, 100)
        
        # 값 표시
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                   f'{val:.1f}%', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        img_buffer.seek(0)
        
        return img_buffer
    
    def _get_status_color(self, value: float, thresholds: tuple = (70, 90)) -> str:
        """값에 따른 상태 색상 반환"""
        if value >= thresholds[1]:
            return self.colors['danger']
        elif value >= thresholds[0]:
            return self.colors['warning']
        return self.colors['primary']
    
    def generate(self, monitoring_data: dict, duration_minutes: int = 5) -> str:
        """PDF 리포트 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"system_report_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )
        
        story = []
        
        # 제목
        story.append(Paragraph("System Resource Monitoring Report", self.styles['CustomTitle']))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Duration: {duration_minutes} minutes",
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 20))
        
        # 요약 테이블
        story.append(Paragraph("📊 Summary Statistics", self.styles['CustomSubtitle']))
        
        summary_data = [
            ["Metric", "Min", "Max", "Average", "Status"]
        ]
        
        # CPU 요약
        if 'cpu' in monitoring_data and monitoring_data['cpu']:
            cpu_data = monitoring_data['cpu']
            avg_cpu = sum(cpu_data) / len(cpu_data) if cpu_data else 0
            status = "🔴 Critical" if avg_cpu >= 85 else ("🟡 Warning" if avg_cpu >= 60 else "🔵 Normal")
            summary_data.append([
                "CPU Usage (%)",
                f"{min(cpu_data):.1f}",
                f"{max(cpu_data):.1f}",
                f"{avg_cpu:.1f}",
                status
            ])
        
        # 메모리 요약
        if 'memory' in monitoring_data and monitoring_data['memory']:
            mem_data = monitoring_data['memory']
            avg_mem = sum(mem_data) / len(mem_data) if mem_data else 0
            status = "🔴 Critical" if avg_mem >= 90 else ("🟡 Warning" if avg_mem >= 70 else "🔵 Normal")
            summary_data.append([
                "Memory Usage (%)",
                f"{min(mem_data):.1f}",
                f"{max(mem_data):.1f}",
                f"{avg_mem:.1f}",
                status
            ])
        
        # GPU 요약
        if 'gpu' in monitoring_data and monitoring_data['gpu']:
            gpu_data = monitoring_data['gpu']
            avg_gpu = sum(gpu_data) / len(gpu_data) if gpu_data else 0
            status = "🔴 Critical" if avg_gpu >= 90 else ("🟡 Warning" if avg_gpu >= 70 else "🔵 Normal")
            summary_data.append([
                "GPU Usage (%)",
                f"{min(gpu_data):.1f}",
                f"{max(gpu_data):.1f}",
                f"{avg_gpu:.1f}",
                status
            ])
        
        # 테이블 스타일
        table = Table(summary_data, colWidths=[3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1F2937')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWHEIGHT', (0, 0), (-1, -1), 25),
        ]))
        story.append(table)
        story.append(Spacer(1, 25))
        
        # CPU 그래프
        if 'cpu' in monitoring_data and monitoring_data['cpu']:
            story.append(Paragraph("🖥️ CPU Usage Over Time", self.styles['CustomSubtitle']))
            cpu_chart = self._create_line_chart(
                monitoring_data['cpu'], 
                "CPU Usage (%)", 
                "Usage (%)",
                self.colors['primary']
            )
            story.append(Image(cpu_chart, width=16*cm, height=6*cm))
            story.append(Spacer(1, 15))
        
        # 메모리 그래프
        if 'memory' in monitoring_data and monitoring_data['memory']:
            story.append(Paragraph("💾 Memory Usage Over Time", self.styles['CustomSubtitle']))
            mem_chart = self._create_line_chart(
                monitoring_data['memory'], 
                "Memory Usage (%)", 
                "Usage (%)",
                '#10B981'
            )
            story.append(Image(mem_chart, width=16*cm, height=6*cm))
            story.append(Spacer(1, 15))
        
        # 네트워크 그래프
        if 'network_upload' in monitoring_data and 'network_download' in monitoring_data:
            story.append(Paragraph("🌐 Network Traffic Over Time", self.styles['CustomSubtitle']))
            net_chart = self._create_dual_line_chart(
                monitoring_data['network_upload'],
                monitoring_data['network_download'],
                "Upload",
                "Download",
                "Network Traffic (KB/s)",
                "Speed (KB/s)",
                '#3B82F6',
                '#10B981'
            )
            story.append(Image(net_chart, width=16*cm, height=6*cm))
            story.append(Spacer(1, 15))
        
        # 디스크 사용량
        if 'disk' in monitoring_data and monitoring_data['disk']:
            story.append(Paragraph("💿 Disk Usage", self.styles['CustomSubtitle']))
            disk_info = monitoring_data['disk']
            labels = [d['mountpoint'] for d in disk_info]
            values = [d['percent'] for d in disk_info]
            
            disk_chart = self._create_bar_chart(
                labels, values,
                "Disk Usage by Partition",
                "Usage (%)"
            )
            story.append(Image(disk_chart, width=16*cm, height=6*cm))
            story.append(Spacer(1, 15))
        
        # 시스템 정보 테이블
        if 'system_info' in monitoring_data:
            story.append(Paragraph("ℹ️ System Information", self.styles['CustomSubtitle']))
            
            sys_info = monitoring_data['system_info']
            info_data = [
                ["Property", "Value"],
            ]
            for key, value in sys_info.items():
                info_data.append([key, str(value)])
            
            info_table = Table(info_data, colWidths=[6*cm, 10*cm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWHEIGHT', (0, 0), (-1, -1), 20),
            ]))
            story.append(info_table)
        
        # PDF 생성
        doc.build(story)
        
        return filepath
