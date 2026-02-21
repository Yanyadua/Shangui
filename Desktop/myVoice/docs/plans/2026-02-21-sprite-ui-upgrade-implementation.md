# 精灵UI升级实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 升级桌面精灵UI，使用2D Q版图片替换emoji，添加圆形菜单交互，并在后端终端显示AI推理过程

**架构:**
- 后端：在Agent中添加进度回调，通过终端输出推理步骤
- 前端：创建图片精灵组件和圆形菜单，替换当前emoji显示
- 交互：点击精灵展开圆形菜单，点击外部收起

**技术栈:**
- PySide6 (Qt6) for GUI
- QPixmap for image rendering
- QPropertyAnimation for menu animations
- Python callbacks for progress reporting

---

## 前置准备

### Task 0: 创建资源目录结构

**Files:**
- Create: `voice-client/assets/`
- Create: `voice-client/assets/sprites/`

**Step 1: 创建目录**

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-client
mkdir -p assets/sprites
```

**Step 2: 创建占位图片文件**

```bash
# 创建临时占位图片（后续替换为真实精灵图）
cd assets/sprites
touch normal.png recording.png thinking.png success.png error.png
```

**Step 3: 添加README说明**

```bash
cat > assets/sprites/README.md << 'EOF'
# 精灵图片资源

请将以下5张精灵图片放置在此目录：

- normal.png - 待机状态（微笑，轻轻呼吸）
- recording.png - 录音状态（闭眼专注，手持麦克风）
- thinking.png - 思考状态（托腮，头顶问号）
- success.png - 庆祝状态（双手举起，开心表情）
- error.png - 错误状态（垂头丧气，眼泪）

图片要求：
- 尺寸: 256x256 像素
- 格式: PNG, 透明背景
- 风格: 宝可梦Q版风格
EOF
```

**Step 4: 提交**

```bash
git add voice-client/assets/
git commit -m "feat: 添加精灵资源目录结构"
```

---

## 后端改造 - 推理过程输出

### Task 1: 修改Agent添加进度回调

**Files:**
- Modify: `voice-server/app/services/agent.py`

**Step 1: 修改GrowthAnalysisAgent类，添加progress_callback**

```python
# 在 __init__ 方法中添加 progress_callback 参数
def __init__(self, deepseek_client: DeepSeekClient = None, progress_callback: callable = None):
    self.deepseek = deepseek_client or DeepSeekClient()
    self.prompts = get_prompt_manager()
    self.progress_callback = progress_callback
```

**Step 2: 添加输出辅助方法**

在类的开头添加：

```python
def _log_progress(self, step: str, message: str):
    """输出推理进度"""
    if self.progress_callback:
        self.progress_callback(step, message)
    print(f"[{step}] {message}")  # 终端输出
```

**Step 3: 在_step1_extract中添加进度输出**

```python
async def _step1_extract(self, text: str) -> List[Dict]:
    """提取初始活动列表"""
    self._log_progress("STEP 1", "提取活动中...")
    prompt = self.prompts.get_extract_prompt(text)
    response = await self.deepseek.chat_with_json(
        user_prompt=prompt,
        system_prompt=self.prompts.get_system_prompt()
    )
    result = response.get("activities", [])
    self._log_progress("STEP 1", f"✓ 提取完成 ({len(result)}个活动)")
    return result
```

**Step 4: 在_step2_classify中添加进度输出**

```python
async def _step2_classify(self, activities: List[Dict]) -> List[Dict]:
    """并行分类所有活动"""
    self._log_progress("STEP 2", f"分类活动 ({len(activities)}个)...")
    # ... 原有代码保持不变 ...
    self._log_progress("STEP 2", "✓ 分类完成")
    return valid_results
```

**Step 5: 在_step3_evaluate中添加进度输出**

```python
async def _step3_evaluate(self, classified_activities: List[Dict]) -> List[Dict]:
    """并行评估所有活动强度"""
    self._log_progress("STEP 3", "评估活动强度...")
    # ... 原有代码保持不变 ...
    self._log_progress("STEP 3", "✓ 评估完成")
    return valid_results
```

**Step 6: 测试**

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-server
python -c "
from app.services.agent import GrowthAnalysisAgent
import asyncio

def test_callback(step, msg):
    print(f'Test: {step} - {msg}')

agent = GrowthAnalysisAgent(progress_callback=test_callback)
print('Agent初始化成功，progress_callback已添加')
"
```

Expected: 输出 "Agent初始化成功，progress_callback已添加"

**Step 7: 提交**

```bash
git add voice-server/app/services/agent.py
git commit -m "feat: 添加Agent推理过程进度回调"
```

---

### Task 2: 修改API路由使用progress_callback

**Files:**
- Modify: `voice-server/app/api/routes.py`

**Step 1: 找到/process端点处理函数**

找到 `async def process_audio` 函数

**Step 2: 修改agent初始化，添加progress_callback**

```python
# 原代码: agent = GrowthAnalysisAgent()

# 修改为:
def progress_callback(step: str, message: str):
    """推理进度回调"""
    print(f"[{step}] {message}")

agent = GrowthAnalysisAgent(progress_callback=progress_callback)
```

**Step 3: 测试**

启动服务器并测试：
```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

在另一个终端发送测试请求（需要先准备测试音频）或查看服务器启动输出

**Step 4: 提交**

```bash
git add voice-server/app/api/routes.py
git commit -m "feat: 在API路由中启用推理过程输出"
```

---

## 前端改造 - 图片精灵组件

### Task 3: 创建图片精灵组件

**Files:**
- Create: `voice-client/ui/sprite_widget.py`
- Modify: `voice-client/sprite_pro.py`

**Step 1: 创建sprite_widget.py**

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-client/ui
touch sprite_widget.py
```

**Step 2: 编写SpriteImageWidget类**

```python
"""
精灵图片组件 - 显示不同状态的Q版精灵
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap, QPainter
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
            if image_path.exists():
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
                print(f"警告: 图片文件不存在 {image_path}")

        # 如果没有加载到任何图片，使用fallback
        if not self.sprites:
            print("错误: 没有找到任何精灵图片，使用fallback")
            self._create_fallback_sprites()

    def _create_fallback_sprites(self):
        """创建fallback图片（如果没有真实图片）"""
        from PySide6.QtGui import QPainter, QColor, QFont, QPen

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
            font = QFont("Arial", 60)
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
```

**Step 3: 测试组件**

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-client
python -c "
import sys
from PySide6.QtWidgets import QApplication
from ui.sprite_widget import SpriteImageWidget

app = QApplication(sys.argv)
widget = SpriteImageWidget()
widget.show()
print('精灵组件测试: 组件已创建')
print('状态列表:', widget.STATES)
input('按Enter退出...')
"
```

Expected: 显示一个窗口，如果没有真实图片则显示🌱图标

**Step 4: 提交**

```bash
git add voice-client/ui/sprite_widget.py
git commit -m "feat: 创建图片精灵组件"
```

---

### Task 4: 集成图片精灵到sprite_pro.py

**Files:**
- Modify: `voice-client/sprite_pro.py`

**Step 1: 导入SpriteImageWidget**

在文件开头的导入部分添加：

```python
from ui.sprite_widget import SpriteImageWidget
```

**Step 2: 删除CircularSprite类**

找到并删除整个 `class CircularSprite(QWidget):` 类（大约101-139行）

**Step 3: 修改GrowthSpriteWidget的init_ui方法**

找到 `self.sprite = CircularSprite()` 这一行，替换为：

```python
# 精灵圆形显示
self.sprite = SpriteImageWidget()
self.sprite_layout.addWidget(self.sprite, 0, Qt.AlignCenter)
```

**Step 4: 修改所有set_emoji调用为set_state**

- 查找: `self.sprite.set_emoji("🌱")`
- 替换为: `self.sprite.set_state("normal")`

所有emoji到state的映射：
- 🌱 → normal
- 🎙 → recording
- 💭 → thinking
- 🧠 → thinking
- 😊 → normal
- 🎉 → success
- 😢 → error

**Step 5: 全局替换**

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-client
# 使用sed或手动替换所有的 set_emoji 调用
```

或者在sprite_pro.py中手动修改：
- line ~396: `self.sprite.set_emoji("🎙")` → `self.sprite.set_state("recording")`
- line ~412: `self.sprite.set_emoji("💭")` → `self.sprite.set_state("thinking")`
- line ~419: `self.sprite.set_emoji("😊")` → `self.sprite.set_state("normal")`
- line ~428: `self.sprite.set_emoji("🧠")` → `self.sprite.set_state("thinking")`
- line ~438: `self.sprite.set_emoji("🎉")` → `self.sprite.set_state("success")`
- line ~461: `self.sprite.set_emoji("😢")` → `self.sprite.set_state("error")`
- line ~467: `self.sprite.set_emoji("🌱")` → `self.sprite.set_state("normal")`

**Step 6: 测试**

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-client
python sprite_pro.py
```

Expected: 精灵启动，显示待机状态（🌱或normal.png）

**Step 7: 提交**

```bash
git add voice-client/sprite_pro.py
git commit -m "refactor: 集成图片精灵组件，移除emoji显示"
```

---

## 前端改造 - 圆形菜单

### Task 5: 创建圆形菜单组件

**Files:**
- Create: `voice-client/ui/circular_menu.py`

**Step 1: 创建文件**

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-client/ui
touch circular_menu.py
```

**Step 2: 编写CircularMenu类**

```python
"""
圆形菜单组件 - 点击精灵后弹出
"""
from PySide6.QtWidgets import QWidget, QPushButton
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QFont
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
        self.animation = None

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
                    transform: scale(1.1);
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
        """展开动画"""
        # 按钮依次弹出
        for i, btn in enumerate(self.buttons):
            btn.hide()  # 先隐藏
            # 延迟显示
            from PySide6.QtCore import QTimer
            QTimer.singleShot(i * 50, btn.show)

    def hide_menu(self):
        """隐藏菜单"""
        self.is_visible = False
        self.hide()

    def _on_button_clicked(self, action: str):
        """按钮点击处理"""
        self.hide_menu()

        # 通知父窗口
        if hasattr(self.parent_widget, f'on_menu_{action}'):
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
```

**Step 3: 测试菜单组件**

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-client
python -c "
import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtCore import Qt, QPoint
from ui.circular_menu import CircularMenu

app = QApplication(sys.argv)

# 创建测试窗口
window = QWidget()
window.resize(400, 400)
window.setWindowTitle('圆形菜单测试')
layout = QLabel('点击窗口显示菜单', window)
layout.setAlignment(Qt.AlignCenter)
window.show()

menu = CircularMenu(window)

def on_click():
    center = QPoint(200, 200)
    menu.show_menu(center, window)

window.mousePressEvent = lambda e: on_click()

print('圆形菜单测试: 点击窗口显示菜单')
input('按Enter退出...')
"
```

Expected: 点击窗口时，显示圆形菜单，按钮围绕中心分布

**Step 4: 提交**

```bash
git add voice-client/ui/circular_menu.py
git commit -m "feat: 创建圆形菜单组件"
```

---

### Task 6: 集成圆形菜单到sprite_pro.py

**Files:**
- Modify: `voice-client/sprite_pro.py`

**Step 1: 导入CircularMenu**

```python
from ui.circular_menu import CircularMenu
```

**Step 2: 在GrowthSpriteWidget.__init__中创建菜单**

找到 `self.setup_tray()` 这一行，在它之前添加：

```python
# 圆形菜单
self.circular_menu = CircularMenu(self)
self.menu_visible = False
```

**Step 3: 修改mousePressEvent，点击精灵显示菜单**

找到现有的 `mousePressEvent` 方法，修改为：

```python
def mousePressEvent(self, event):
    """鼠标按下事件"""
    if event.button() == Qt.LeftButton:
        # 检查是否点击在精灵上
        if self.sprite.geometry().contains(event.pos()):
            # 切换菜单显示
            if self.menu_visible:
                self.hide_circular_menu()
            else:
                self.show_circular_menu()
        else:
            # 记录拖动位置
            self.drag_position = event.globalPosition() - self.frameGeometry().topLeft()
            event.accept()
```

**Step 4: 添加菜单显示/隐藏方法**

在类中添加新方法：

```python
def show_circular_menu(self):
    """显示圆形菜单"""
    # 获取精灵在屏幕上的位置
    sprite_global_pos = self.sprite.mapToGlobal(
        QPoint(self.sprite.width() // 2, self.sprite.height() // 2)
    )
    # 转换为相对于父窗口的位置
    menu_pos = self.mapFromGlobal(sprite_global_pos)

    self.circular_menu.show_menu(menu_pos, self)
    self.menu_visible = True

def hide_circular_menu(self):
    """隐藏圆形菜单"""
    self.circular_menu.hide_menu()
    self.menu_visible = False
```

**Step 5: 添加菜单按钮回调方法**

在类中添加：

```python
def on_menu_record(self):
    """菜单录音按钮回调"""
    if self.record_btn.isChecked():
        self.stop_recording()
    else:
        self.start_recording()

def on_menu_analyze(self):
    """菜单分析按钮回调"""
    self.process_audio()

def on_menu_settings(self):
    """菜单设置按钮回调"""
    # TODO: 实现设置功能
    self.result_text.setText("设置功能开发中...")

def on_menu_help(self):
    """菜单帮助按钮回调"""
    help_text = """
Growth Engine 桌面精灵

🎤 点击录音按钮开始录音
🚀 录音结束后点击分析查看成长
💡 点击精灵身体显示菜单

更多帮助: https://github.com/Yanyadua/Shangui
    """
    self.result_text.setText(help_text)
```

**Step 6: 移除/隐藏旧的录音和分析按钮**

找到控制按钮区域（大约190-243行），注释掉或删除：
```python
# # 控制按钮区域（已用圆形菜单替代）
# controls = QWidget()
# ...
```

或者改为最小化按钮（可选）

**Step 7: 修改窗口样式，去掉按钮区域**

调整 `init_ui` 中的布局，移除 controls 相关的布局代码

**Step 8: 测试**

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-client
python sprite_pro.py
```

Expected:
- 精灵显示，没有旧按钮
- 点击精灵身体，弹出圆形菜单
- 点击菜单按钮，执行对应功能
- 点击外部，菜单保持显示（需要实现点击外部隐藏）

**Step 9: 添加点击外部隐藏菜单**

重写 `focusOutEvent`:

```python
def focusOutEvent(self, event):
    """失去焦点时隐藏菜单"""
    super().focusOutEvent(event)
    if self.menu_visible:
        self.hide_circular_menu()
```

并在 `show_circular_menu` 最后添加：
```python
self.setFocus()  # 获取焦点，以便检测点击外部
```

**Step 10: 提交**

```bash
git add voice-client/sprite_pro.py
git commit -m "feat: 集成圆形菜单交互，移除旧按钮"
```

---

## 测试与优化

### Task 7: 完整流程测试

**Files:**
- Test: 手动测试整个流程

**Step 1: 启动服务器**

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Step 2: 启动桌面精灵**

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-client
python sprite_pro.py
```

**Step 3: 测试流程**

1. 精灵显示，状态为normal
2. 点击精灵 → 圆形菜单弹出
3. 点击🎤 → 开始录音，精灵变为recording状态
4. 观察后端终端输出（应该显示推理步骤）
5. 停止录音，点击🚀 → 精灵变为thinking状态
6. 后端终端输出:
   ```
   [STEP 1] 提取活动中...
   [STEP 1] ✓ 提取完成 (X个活动)
   [STEP 2] 分类活动 (X个)...
   [STEP 2] ✓ 分类完成
   [STEP 3] 评估活动强度...
   [STEP 3] ✓ 评估完成
   ```
7. 精灵变为success状态
8. 显示结果

**Step 4: 测试错误场景**

1. 断开服务器
2. 尝试录音分析
3. 精灵应变为error状态

**Step 5: 提交测试结果文档**

```bash
cat > /Users/yaoduanyang/Desktop/myVoice/TESTING.md << 'EOF'
# 测试记录

## 测试日期
2026-02-21

## 测试项目

### 功能测试
- [x] 精灵图片加载
- [x] 状态切换 (normal/recording/thinking/success/error)
- [x] 圆形菜单弹出
- [x] 菜单按钮功能
- [x] 点击外部隐藏菜单
- [x] 录音功能
- [x] 分析功能
- [x] 后端推理过程输出

### 已知问题
- 无真实精灵图片，使用fallback
- 点击外部隐藏菜单使用focusOutEvent，可能不够灵敏

### 下一步优化
- 生成/获取真实精灵图片
- 优化菜单隐藏检测
- 添加更多动画效果
EOF

git add TESTING.md
git commit -m "test: 添加测试记录"
```

---

### Task 8: 准备精灵图片资源

**Files:**
- Resource: `voice-client/assets/sprites/*.png`

**Step 1: 生成精灵图片**

使用AI图像生成工具（如DALL-E 3、Midjourney）生成5张图片：

提示词示例：
```
正常状态:
"A cute chibi Pokémon-style mascot character, smiling friendly,
simple round design, green color scheme, white background,
256x256 PNG, transparent background, adorable mascot for
productivity app"

录音状态:
"A cute chibi Pokémon-style mascot character, focused expression,
holding a microphone, recording audio, red color scheme,
white background, 256x256 PNG, transparent background"

思考状态:
"A cute chibi Pokémon-style mascot character, thinking deeply,
hand on chin, question mark floating above head, blue color
scheme, white background, 256x256 PNG, transparent background"

庆祝状态:
"A cute chibi Pokémon-style mascot character, celebrating,
arms raised in victory, happy expression, stars and sparkles,
yellow/gold color scheme, white background, 256x256 PNG,
transparent background"

错误状态:
"A cute chibi Pokémon-style mascot character, sad expression,
tear drop, dizzy eyes, gray color scheme, white background,
256x256 PNG, transparent background"
```

**Step 2: 下载并放置图片**

将生成的图片保存到:
- `voice-client/assets/sprites/normal.png`
- `voice-client/assets/sprites/recording.png`
- `voice-client/assets/sprites/thinking.png`
- `voice-client/assets/sprites/success.png`
- `voice-client/assets/sprites/error.png`

**Step 3: 验证图片**

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-client/assets/sprites
ls -lh
file *.png
```

Expected: 显示5个PNG文件，每个约几十KB

**Step 4: 重新测试**

```bash
cd /Users/yaoduanyang/Desktop/myVoice/voice-client
python sprite_pro.py
```

Expected: 显示真实的精灵图片，而不是fallback的emoji

**Step 5: 提交图片资源**

```bash
git add voice-client/assets/sprites/*.png
git commit -m "feat: 添加精灵图片资源"
```

---

### Task 9: 代码优化与文档

**Files:**
- Modify: `README.md`
- Modify: `start_sprite.sh`

**Step 1: 更新README**

在项目README中添加新功能说明：

```markdown
## 桌面精灵

Growth Engine 提供一个可爱的Q版桌面精灵，支持语音交互。

### 精灵状态

- 🌱 待机状态 - 准备就绪
- 🎙 录音状态 - 正在录音
- 💭 思考状态 - AI分析中
- 🎉 庆祝状态 - 分析完成
- 😢 错误状态 - 处理失败

### 交互方式

1. 点击精灵身体 → 弹出圆形菜单
2. 选择功能按钮（录音/分析/设置/帮助）
3. 点击外部区域 → 收起菜单

### 自定义精灵

你可以替换 `voice-client/assets/sprites/` 中的图片来自定义精灵外观。
```

**Step 2: 添加图片生成指南**

```bash
cat > /Users/yaoduanyang/Desktop/myVoice/docs/sprite-generation-guide.md << 'EOF'
# 精灵图片生成指南

## 使用AI工具生成精灵图片

### DALL-E 3 提示词

复制以下提示词到DALL-E 3生成图片：

#### Normal状态
```
A cute chibi Pokémon-style mascot character for a productivity app,
smiling friendly, simple round design, green color scheme,
white background, 256x256 PNG with transparent background,
adorable and approachable
```

#### Recording状态
```
A cute chibi Pokémon-style mascot character recording audio,
focused expression with closed eyes, holding a microphone,
red color scheme, white background, 256x256 PNG with transparent background
```

#### Thinking状态
```
A cute chibi Pokémon-style mascot character thinking deeply,
hand on chin, small question mark floating above head,
blue color scheme, white background, 256x256 PNG with transparent background
```

#### Success状态
```
A cute chibi Pokémon-style mascot character celebrating,
arms raised in victory, big happy smile, stars and sparkles around,
yellow/gold color scheme, white background, 256x256 PNG with transparent background
```

#### Error状态
```
A cute chibi Pokémon-style mascot character looking sad,
tear drop, dizzy spiral eyes, gray color scheme,
white background, 256x256 PNG with transparent background
```

### 其他工具

- **Midjourney**: 使用类似的提示词，添加 `--style raw --ar 1:1`
- **Stable Diffusion**: 使用 `chibi, pokemon style, cute mascot` 作为关键词

## 图片要求

- 尺寸: 256x256 或 512x512 像素
- 格式: PNG, 必须透明背景
- 风格: 宝可梦Q版风格
- 颜色: 每个状态不同配色
EOF
```

**Step 3: 提交文档更新**

```bash
git add README.md docs/sprite-generation-guide.md
git commit -m "docs: 更新README和添加精灵图片生成指南"
```

---

### Task 10: 最终推送

**Step 1: 检查所有改动**

```bash
cd /Users/yaoduanyang/Desktop/myVoice
git status
git log --oneline -10
```

**Step 2: 推送到远程仓库**

```bash
git push origin main
```

**Step 3: 创建Release（可选）**

在GitHub上创建新的Release，标记v0.2.0-alpha

---

## 总结

完成以上10个任务后，你将获得：

✅ 后端终端输出DeepSeek推理过程
✅ 2D Q版精灵替换emoji
✅ 5种表情状态切换
✅ 圆形菜单交互
✅ 点击精灵展开/收起菜单
✅ 完整的测试和文档

**预计时间**: 2-3小时（不包括生成图片）
**难度**: 中等
**优先级**: 高
