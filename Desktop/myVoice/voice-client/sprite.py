"""
Growth Engine 桌面精灵
一个可爱的桌面小助手,帮助你记录成长
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QPoint
from PySide6.QtGui import QPixmap, QPainter, QBrush, QColor, QFont, QIcon, QAction
import asyncio
from pathlib import Path
import tempfile

# 导入 API 客户端
try:
    from services.api_client import APIClient
except ImportError:
    from voice_client.services.api_client import APIClient


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

            # 保存到临时文件
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


class GrowthSprite(QWidget):
    """成长精灵 - 桌面小助手"""

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.recorder = None
        self.audio_file_path = None
        self.process_worker = None

        self.init_ui()
        self.set_window_style()

        # 精灵动画状态
        self.bounce_offset = 0
        self.bounce_direction = 1
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate)
        self.animation_timer.start(50)  # 20fps

    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("Growth Engine - 桌面精灵 🌱")
        self.setFixedSize(280, 400)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 精灵显示区
        self.sprite_label = QLabel()
        self.sprite_label.setMinimumHeight(150)
        self.sprite_label.setAlignment(Qt.AlignCenter)
        self.sprite_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e8f5e9, stop:1 #c8e6c9);
                border: 2px solid #81c784;
                border-radius: 15px;
                font-size: 60px;
            }
        """)
        self.sprite_label.setText("🌱")

        # 状态显示
        self.status_label = QLabel("🌱 准备就绪,开始记录成长吧!")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #2e7d32;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
        """)

        # 录音按钮
        self.record_button = QPushButton("🎤 开始录音")
        self.record_button.setCheckable(True)
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #66bb6a;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #43a047;
            }
            QPushButton:checked {
                background-color: #ef5350;
            }
            QPushButton:disabled {
                background-color: #bdbdbd;
            }
        """)
        self.record_button.clicked.connect(self.toggle_recording)

        # 处理按钮
        self.process_button = QPushButton("🚀 分析成长")
        self.process_button.setEnabled(False)
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #42a5f5;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e88e5;
            }
            QPushButton:disabled {
                background-color: #bdbdbd;
            }
        """)
        self.process_button.clicked.connect(self.process_audio)

        # 结果显示
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(120)
        self.result_text.setPlaceholderText("📊 成长分析结果将显示在这里...")
        self.result_text.setStyleSheet("""
            QTextEdit {
                background: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 11px;
            }
        """)

        # 添加到布局
        layout.addWidget(self.sprite_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.record_button)
        layout.addWidget(self.process_button)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

        # 设置系统托盘
        self.setup_tray()

    def set_window_style(self):
        """设置窗口样式"""
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |  # 置顶
            Qt.FramelessWindowHint |      # 无边框
            Qt.Tool                      # 工具窗口
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f1f8e9, stop:1 #dcedc8);
                border: 2px solid #81c784;
                border-radius: 20px;
            }
        """)

    def setup_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)

        # 创建托盘菜单
        tray_menu = QMenu()

        show_action = QAction("显示精灵", self)
        show_action.triggered.connect(self.show)

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(QApplication.instance().quit)

        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def animate(self):
        """精灵动画"""
        self.bounce_offset += self.bounce_direction * 2

        if abs(self.bounce_offset) > 10:
            self.bounce_direction *= -1

        self.sprite_label.move(0, self.bounce_offset)

    def toggle_recording(self):
        """切换录音状态"""
        if self.record_button.isChecked():
            # 开始录音
            self.record_button.setText("⏹ 停止录音")
            self.status_label.setText("🎤 正在录音...")
            self.sprite_label.setText("🎙")

            self.recorder = AudioRecorder()
            self.recorder.finished.connect(self.on_recording_finished)
            self.recorder.start()

            # 同时启动一个定时器来限制录音时长
            QTimer.singleShot(60000, self.stop_recording)  # 最多60秒
        else:
            # 停止录音
            self.stop_recording()

    def stop_recording(self):
        """停止录音"""
        if self.recorder:
            self.record_button.setChecked(False)
            self.record_button.setText("🎤 开始录音")
            self.status_label.setText("⏳ 处理中...")
            self.sprite_label.setText("💭")
            self.recorder.stop()
            self.recorder.wait()

    def on_recording_finished(self, audio_path: str):
        """录音完成"""
        self.audio_file_path = audio_path
        self.process_button.setEnabled(True)
        self.status_label.setText("✅ 录音完成,可以分析啦!")
        self.sprite_label.setText("😊")

    def process_audio(self):
        """处理音频"""
        if not self.audio_file_path:
            return

        self.process_button.setEnabled(False)
        self.status_label.setText("🤖 AI 正在分析...")
        self.sprite_label.setText("🧠")

        worker = ProcessWorker(self.audio_file_path, self.api_client)
        worker.finished.connect(self.on_process_finished)
        worker.error.connect(self.on_process_error)
        worker.start()

    def on_process_finished(self, result: dict):
        """处理完成"""
        self.status_label.setText("✅ 分析完成!")
        self.sprite_label.setText("🎉")

        # 格式化显示结果
        output = []
        output.append(f"📝: {result['text'][:50]}...")
        output.append(f"\n🎯 活动列表 ({len(result['activities'])}个):")

        for i, activity in enumerate(result['activities'], 1):
            emoji = {"Learning Input": "📚", "Active Practice": "💪",
                   "Problem Solving": "🔧", "Production Output": "📝",
                   "System Improvement": "⚙", "Energy Management": "💤"}.get(activity['type'], "📌")
            output.append(f"  {i}. {emoji} {activity['topic']} (强度:{activity['intensity']:.1f})")

        output.append("\n📊 成长增量:")
        for dimension, value in result['delta'].items():
            if value > 0:
                emoji = {"knowledge_intake": "🧠", "skill_fluency": "⚡",
                       "complexity_handling": "🎯", "system_thinking": "🔮",
                       "execution": "🏃"}.get(dimension, "📈")
                output.append(f"  {emoji} {dimension}: {value:.3f}")

        self.result_text.setText("\n".join(output))

        # 3秒后重置状态
        QTimer.singleShot(3000, lambda: self.reset_status())

    def on_process_error(self, error_msg: str):
        """处理错误"""
        self.status_label.setText("❌ 处理失败")
        self.sprite_label.setText("😢")
        self.result_text.setText(f"错误: {error_msg}")
        self.process_button.setEnabled(True)

    def reset_status(self):
        """重置状态"""
        self.status_label.setText("🌱 准备就绪,继续记录成长吧!")
        self.sprite_label.setText("🌱")
        self.process_button.setEnabled(True)
        self.audio_file_path = None

    def mousePressEvent(self, event):
        """鼠标按下事件 - 用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖动窗口"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition() - self.drag_position)
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出程序

    sprite = GrowthSprite()
    sprite.show()

    sys.exit(app.exec())
