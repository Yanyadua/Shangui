"""
精灵图片组件 - 显示不同状态的Q版精灵
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt, QSize
from pathlib import Path


class SpriteImageWidget(QWidget):
    """显示精灵图片的组件"""

    # 状态定义
    STATES = {
        'normal': '待机',
        'recording': '录音中',
        'thinking': '思考中',
        'success': '完成',
        'error': '错误'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sprites = {}
        self.current_state = 'normal'
        self.load_sprites()
        self.setFixedSize(200, 200)

    def load_sprites(self):
        """加载所有精灵图片"""
        assets_dir = Path(__file__).parent.parent / "assets" / "sprites"

        for state in self.STATES.keys():
            image_path = assets_dir / f"{state}.png"
            if image_path.exists() and image_path.stat().st_size > 0:
                pixmap = QPixmap(str(image_path))
                if not pixmap.isNull():
                    # 缩放到200x200，保持比例
                    scaled = pixmap.scaled(
                        200, 200,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.sprites[state] = scaled
                else:
                    print(f"警告: 无法加载图片 {image_path}")
            else:
                print(f"警告: 图片文件不存在或为空 {image_path}")

        # 如果没有加载到任何图片，使用fallback
        if not self.sprites:
            print("提示: 没有找到真实精灵图片，使用emoji fallback")
            self._create_fallback_sprites()

    def _create_fallback_sprites(self):
        """创建fallback图片（如果没有真实图片）"""
        def create_placeholder(text, color):
            pixmap = QPixmap(200, 200)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            # 绘制圆形背景
            painter.setBrush(QColor(color))
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.drawEllipse(10, 10, 180, 180)

            # 绘制文字
            painter.setPen(QColor(255, 255, 255))
            font = QFont("Apple Color Emoji", 60)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, text)

            painter.end()
            return pixmap

        self.sprites['normal'] = create_placeholder("🌱", "#81c784")
        self.sprites['recording'] = create_placeholder("🎙", "#ef5350")
        self.sprites['thinking'] = create_placeholder("💭", "#64b5f6")
        self.sprites['success'] = create_placeholder("🎉", "#ffd54f")
        self.sprites['error'] = create_placeholder("😢", "#90a4ae")

    def set_state(self, state: str):
        """设置精灵状态"""
        if state in self.STATES:
            self.current_state = state
            self.update()
        else:
            print(f"警告: 未知状态 {state}")

    def paintEvent(self, event):
        """绘制精灵"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.current_state in self.sprites:
            pixmap = self.sprites[self.current_state]
            # 居中绘制
            x = (self.width() - pixmap.width()) // 2
            y = (self.height() - pixmap.height()) // 2
            painter.drawPixmap(x, y, pixmap)
        else:
            # Fallback: 绘制占位符
            painter.setBrush(Qt.gray)
            painter.drawEllipse(0, 0, self.width(), self.height())
