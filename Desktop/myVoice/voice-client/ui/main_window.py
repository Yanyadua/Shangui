import sys
import tempfile
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QLabel, QMessageBox
)
from PySide6.QtCore import QThread, Signal
import pyaudio
import wave

# 修复导入路径
try:
    from ..services.api_client import APIClient
except ImportError:
    from services.api_client import APIClient


class AudioRecorder(QThread):
    """音频录制线程"""
    finished = Signal(str)  # 录制完成,返回文件路径

    def __init__(self, duration_seconds: int = 60):
        super().__init__()
        self.duration = duration_seconds
        self.is_recording = True

    def run(self):
        """录制音频"""
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
                data = stream.read(chunk)
                frames.append(data)

            stream.stop_stream()
            stream.close()

            # 保存到临时文件
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".wav"
            ) as tmp_file:
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
        """停止录制"""
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
        """处理音频"""
        try:
            result = self.api_client.process_audio(self.audio_path)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.recorder = None
        self.audio_file_path = None

        self.setup_ui()

    def setup_ui(self):
        """设置 UI"""
        self.setWindowTitle("Growth Engine - 语音成长记录")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 录音按钮
        self.record_button = QPushButton("开始录音")
        self.record_button.setCheckable(True)
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)

        # 状态标签
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)

        # 处理按钮
        self.process_button = QPushButton("上传并处理")
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.process_audio)
        layout.addWidget(self.process_button)

        # 结果显示
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("处理结果将显示在这里...")
        layout.addWidget(self.result_text)

    def toggle_recording(self):
        """切换录音状态"""
        if self.record_button.isChecked():
            # 开始录音
            self.record_button.setText("停止录音")
            self.status_label.setText("录音中...")

            self.recorder = AudioRecorder()
            self.recorder.finished.connect(self.on_recording_finished)
            self.recorder.start()
        else:
            # 停止录音
            self.record_button.setText("开始录音")
            self.status_label.setText("处理中...")

            if self.recorder:
                self.recorder.stop()
                self.recorder.wait()

    def on_recording_finished(self, audio_path: str):
        """录音完成"""
        self.audio_file_path = audio_path
        self.process_button.setEnabled(True)
        self.status_label.setText(f"录音完成: {audio_path}")

    def process_audio(self):
        """处理音频"""
        if not self.audio_file_path:
            return

        self.status_label.setText("上传中...")
        self.process_button.setEnabled(False)

        worker = ProcessWorker(self.audio_file_path, self.api_client)
        worker.finished.connect(self.on_process_finished)
        worker.error.connect(self.on_process_error)
        worker.start()

    def on_process_finished(self, result: dict):
        """处理完成"""
        self.status_label.setText("处理完成")

        # 格式化显示结果
        output = []
        output.append(f"📝 转写文本:\n{result['text']}\n")
        output.append(f"📅 日期: {result['date']}\n")
        output.append("\n🎯 活动列表:")
        for i, activity in enumerate(result['activities'], 1):
            output.append(
                f"  {i}. [{activity['type']}] {activity['topic']}\n"
                f"     强度: {activity['intensity']:.2f}, "
                f"时长: {activity['duration_estimate']:.1f}h"
            )

        output.append("\n📊 成长增量 (Delta):")
        for dimension, value in result['delta'].items():
            output.append(f"  - {dimension}: {value:.3f}")

        self.result_text.setText("\n".join(output))

    def on_process_error(self, error_msg: str):
        """处理错误"""
        self.status_label.setText("处理失败")
        QMessageBox.critical(self, "错误", f"处理失败: {error_msg}")
        self.process_button.setEnabled(True)