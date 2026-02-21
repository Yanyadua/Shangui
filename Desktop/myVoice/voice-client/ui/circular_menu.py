"""
圆形菜单组件 - 点击精灵后弹出
"""
from PySide6.QtWidgets import QWidget, QPushButton
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QPainter, QColor, QPen
import math


class CircularMenu(QWidget):
    """圆形弹出菜单"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = []
        self.center_pos = QPoint(0, 0)
        self.radius = 100
        self.button_radius = 30
        self.is_visible = False
        self.parent_widget = None

        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(300, 300)

        # 初始化按钮
        self._init_buttons()

    def _init_buttons(self):
        """初始化菜单按钮"""
        # 定义按钮: (emoji, 回调方法名, 颜色)
        button_configs = [
            ("🎤", "record", "#ef5350"),    # 录音 - 红色
            ("🚀", "analyze", "#42a5f5"),  # 分析 - 蓝色
            ("⚙️", "settings", "#ffd54f"),  # 设置 - 黄色
            ("❓", "help", "#81c784"),      # 帮助 - 绿色
        ]

        for emoji, action, color in button_configs:
            btn = QPushButton(emoji, self)
            btn.setFixedSize(self.button_radius * 2, self.button_radius * 2)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 3px solid white;
                    border-radius: {self.button_radius}px;
                    font-size: 24px;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    border: 3px solid #ffd54f;
                }}
                QPushButton:pressed {{
                    background-color: {color};
                    border: 3px solid #bdbdbd;
                }}
            """)
            btn.clicked.connect(lambda checked, a=action: self._on_button_clicked(a))
            self.buttons.append(btn)

        # 初始隐藏所有按钮
        for btn in self.buttons:
            btn.hide()

    def show_menu(self, center_pos: QPoint, parent_widget):
        """显示菜单"""
        self.center_pos = center_pos
        self.parent_widget = parent_widget

        # 计算菜单位置（使其居中于精灵）
        menu_x = center_pos.x() - self.width() // 2
        menu_y = center_pos.y() - self.height() // 2
        self.move(menu_x, menu_y)

        # 计算按钮位置（圆形分布）
        self._layout_buttons()

        # 显示窗口和按钮
        self.show()
        self.is_visible = True

        # 播放展开动画
        self._animate_show()

    def _layout_buttons(self):
        """计算按钮位置（圆形分布）"""
        center_x = self.width() // 2
        center_y = self.height() // 2

        # 将按钮分布在圆周上（从上方开始，顺时针）
        num_buttons = len(self.buttons)
        for i, btn in enumerate(self.buttons):
            # 角度：从-90度（顶部）开始
            angle = -90 + (360 * i / num_buttons)
            angle_rad = math.radians(angle)

            # 计算位置
            x = center_x + self.radius * math.cos(angle_rad) - self.button_radius
            y = center_y + self.radius * math.sin(angle_rad) - self.button_radius
            btn.move(int(x), int(y))
            btn.show()

    def _animate_show(self):
        """展开动画 - 按钮依次弹出"""
        for i, btn in enumerate(self.buttons):
            btn.hide()  # 先隐藏
            # 延迟显示
            QTimer.singleShot(i * 50, btn.show)

    def hide_menu(self):
        """隐藏菜单"""
        self.is_visible = False
        self.hide()

    def _on_button_clicked(self, action: str):
        """按钮点击处理"""
        self.hide_menu()

        # 通知父窗口
        if self.parent_widget and hasattr(self.parent_widget, f'on_menu_{action}'):
            method = getattr(self.parent_widget, f'on_menu_{action}')
            method()

    def paintEvent(self, event):
        """绘制背景（可选：添加半透明圆形背景）"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制半透明背景圆
        center_x = self.width() // 2
        center_y = self.height() // 2

        painter.setBrush(QColor(0, 0, 0, 80))  # 半透明黑色
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            center_x - self.radius - 20,
            center_y - self.radius - 20,
            self.radius * 2 + 40,
            self.radius * 2 + 40
        )
