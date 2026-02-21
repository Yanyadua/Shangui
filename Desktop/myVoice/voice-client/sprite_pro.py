"""
Growth Engine 专业桌面精灵 v2.0
使用图片和更精美的UI设计
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                                QPushButton, QLabel, QTextEdit, QSystemTrayIcon,
                                QMenu, QGraphicsDropShadowEffect, QFrame)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QPoint
from PySide6.QtGui import (QPixmap, QPainter, QBrush, QColor, QFont, QIcon,
                        QAction, QRadialGradient, QPen, QPolygon)
import asyncio
from pathlib import Path
import tempfile
import math

try:
    from services.api_client import APIClient
    from ui.sprite_widget import SpriteImageWidget
except ImportError:
    from voice_client.services.api_client import APIClient
    from voice_client.ui.sprite_widget import SpriteImageWidget


class AudioRecorder(QThread):
    """音频录制线程"""
    finished = Signal(str)

    def __init__(self):
        super().__init__()
        self.is_recording = False

    def run(self):
        import pyaudio
        import wave

        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 1
        fs = 44100

        p = pyaudio.PyAudio()

        try:
            stream = p.open(
                format=sample_format,
                channels=channels,
                rate=fs,
                frames_per_buffer=chunk,
                input=True
            )

            frames = []
            while self.is_recording:
                try:
                    data = stream.read(chunk)
                    frames.append(data)
                except:
                    break

            stream.stop_stream()
            stream.close()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_path = tmp_file.name

            with wave.open(tmp_path, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(p.get_sample_size(sample_format))
                wf.setframerate(fs)
                wf.writeframes(b''.join(frames))

            self.finished.emit(tmp_path)

        finally:
            p.terminate()

    def stop(self):
        self.is_recording = False


class ProcessWorker(QThread):
    """处理工作线程"""
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, audio_path: str, api_client: APIClient):
        super().__init__()
        self.audio_path = audio_path
        self.api_client = api_client

    def run(self):
        try:
            result = self.api_client.process_audio(self.audio_path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class GrowthSpriteWidget(QWidget):
    """成长精灵主窗口"""

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.recorder = None
        self.process_worker = None
        self.audio_file_path = None

        # 动画相关
        self._float_offset = 0
        self._float_direction = 1

        self.init_ui()
        self.set_window_style()
        self.setup_animations()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 精灵区域
        sprite_container = QWidget()
        self.sprite_layout = QVBoxLayout(sprite_container)
        self.sprite_layout.setContentsMargins(15, 20, 15, 15)
        self.sprite_layout.setSpacing(15)

        # 精灵图片显示
        self.sprite = SpriteImageWidget()
        self.sprite_layout.addWidget(self.sprite, 0, Qt.AlignCenter)

        # 状态文字
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #2e7d32;
                font-size: 13px;
                font-weight: bold;
                background: transparent;
                padding: 5px;
            }
        """)
        self.sprite_layout.addWidget(self.status_label)

        # 控制按钮区域
        controls = QWidget()
        control_layout = QHBoxLayout(controls)
        control_layout.setContentsMargins(10, 5, 10, 5)
        control_layout.setSpacing(8)

        self.record_btn = QPushButton("🎤")
        self.record_btn.setFixedSize(45, 45)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66bb6a, stop:1 #43a047);
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 18px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #81c784, stop:1 #66bb6a);
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ef5350, stop:1 #c62828);
            }
        """)
        self.record_btn.setCheckable(True)
        self.record_btn.clicked.connect(self.toggle_recording)

        self.process_btn = QPushButton("🚀")
        self.process_btn.setFixedSize(45, 45)
        self.process_btn.setEnabled(False)
        self.process_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #42a5f5, stop:1 #1e88e5);
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 18px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #64b5f6, stop:1 #42a5f5);
            }
            QPushButton:disabled {
                background: #bdbdbd;
                color: #757575;
            }
        """)
        self.process_btn.clicked.connect(self.process_audio)

        control_layout.addWidget(self.record_btn)
        control_layout.addWidget(self.process_btn)
        control_layout.addStretch()

        # 最小化/关闭按钮
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,100);
                color: #666;
                border: none;
                border-radius: 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,200);
                color: #333;
            }
        """)
        close_btn.clicked.connect(self.close)
        control_layout.addWidget(close_btn)

        # 添加所有组件到布局
        layout.addWidget(sprite_container)
        layout.addWidget(controls)

        # 结果显示区
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(100)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background: rgba(255,255,255,0.9);
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

        # 设置阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        # 设置系统托盘
        self.setup_tray()

    def set_window_style(self):
        """设置窗口样式"""
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(232, 245, 233, 0.95),
                    stop:1 rgba(227, 243, 219, 0.95));
                border: 2px solid rgba(129, 199, 132, 0.5);
                border-radius: 25px;
            }
        """)

    def setup_animations(self):
        """设置动画"""
        self.float_timer = QTimer()
        self.float_timer.timeout.connect(self.animate_float)
        self.float_timer.start(50)  # 20fps

        self.sprite.animation_timer = QTimer()
        self.sprite.animation_timer.timeout.connect(self.animate_sprite)
        self.sprite.animation_timer.start(100)

    def animate_float(self):
        """浮动动画"""
        self._float_offset += self._float_direction * 0.3

        if abs(self._float_offset) > 3:
            self._float_direction *= -1

        # 应用浮动效果
        from PySide6.QtCore import QPropertyAnimation
        # 简单的position更新
        current_pos = self.pos()
        self.move(current_pos.x(), current_pos.y() + self._float_offset)

    def animate_sprite(self):
        """精灵动画 - 图片精灵不需要内部动画，保留空函数避免报错"""
        pass

    def setup_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)

        # 创建简单图标
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制简单的叶子图标
        gradient = QRadialGradient(32, 32, 5, 32, 32)
        gradient.setColorAt(0, QColor(129, 199, 132))
        gradient.setColorAt(1, QColor(76, 175, 80))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(16, 16, 32, 32)

        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawLine(32, 20, 32, 44)
        painter.drawLine(24, 28, 32, 32)
        painter.drawLine(40, 28, 32, 32)

        painter.end()

        self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.setToolTip("Growth Engine - 桌面精灵")

        tray_menu = QMenu()

        show_action = QAction("显示精灵", self)
        show_action.triggered.connect(self.show)

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(QApplication.instance().quit)

        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def toggle_recording(self):
        """切换录音状态"""
        if self.record_btn.isChecked():
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """开始录音"""
        self.status_label.setText("正在录音...")
        self.sprite.set_state("recording")
        self.process_btn.setEnabled(False)

        self.recorder = AudioRecorder()
        self.recorder.finished.connect(self.on_recording_finished)
        self.recorder.start()

        # 60秒后自动停止
        QTimer.singleShot(60000, self.stop_recording)

    def stop_recording(self):
        """停止录音"""
        if self.recorder:
            self.record_btn.setChecked(False)
            self.recorder.stop()
            self.status_label.setText("处理中...")
            self.sprite.set_state("thinking")

    def on_recording_finished(self, audio_path: str):
        """录音完成"""
        self.audio_file_path = audio_path
        self.process_btn.setEnabled(True)
        self.status_label.setText("录音完成")
        self.sprite.set_state("normal")

    def process_audio(self):
        """处理音频"""
        if not self.audio_file_path:
            return

        self.process_btn.setEnabled(False)
        self.status_label.setText("AI分析中...")
        self.sprite.set_state("thinking")

        worker = ProcessWorker(self.audio_file_path, self.api_client)
        worker.finished.connect(self.on_process_finished)
        worker.error.connect(self.on_process_error)
        worker.start()

    def on_process_finished(self, result: dict):
        """处理完成"""
        self.status_label.setText("分析完成!")
        self.sprite.set_state("success")

        # 格式化结果
        lines = []
        lines.append(f"📝 {result['text'][:40]}...")
        lines.append(f"\n🎯 {len(result['activities'])} 个活动:")

        for i, act in enumerate(result['activities'][:3], 1):
            lines.append(f"{i}. {act['topic']}")

        lines.append(f"\n📊 成长:")
        total = sum(result['delta'].values())
        lines.append(f"总计: {total:.3f}")

        self.result_text.setText("\n".join(lines))

        # 5秒后重置
        QTimer.singleShot(5000, self.reset_state)

    def on_process_error(self, error_msg: str):
        """处理错误"""
        self.status_label.setText("处理失败")
        self.sprite.set_state("error")
        self.result_text.setText(f"错误: {error_msg}")
        self.process_btn.setEnabled(True)

    def reset_state(self):
        """重置状态"""
        self.status_label.setText("准备就绪")
        self.sprite.set_state("normal")
        self.process_btn.setEnabled(True)
        self.audio_file_path = None

    def mousePressEvent(self, event):
        """鼠标按下 - 拖动"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动 - 拖动"""
        if event.buttons() == Qt.LeftButton:
            pos = event.globalPosition() - self.drag_position
            self.move(pos.toPoint())
            event.accept()

    def closeEvent(self, event):
        """关闭窗口 - 隐藏到托盘而不是退出"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Growth Engine",
            "精灵已最小化到托盘，双击图标恢复",
            QSystemTrayIcon.Information,
            2000
        )


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    sprite = GrowthSpriteWidget()
    sprite.show()

    sys.exit(app.exec())
