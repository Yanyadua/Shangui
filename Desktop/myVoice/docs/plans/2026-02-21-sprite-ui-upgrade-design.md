# Growth Engine 精灵UI升级设计方案

**日期**: 2026-02-21
**目标**: 升级桌面精灵UI，使用2D Q版角色和圆形菜单交互

---

## 需求总结

### 1. 后端推理过程可见化
- 在后端终端输出DeepSeek推理步骤
- 使用简洁模式，不刷屏但清晰可读

### 2. 2D Q版精灵
- AI生成的原创宝可梦风格角色
- 替换当前的emoji显示

### 3. 5种表情状态
- 待机状态（normal）- 默认状态
- 录音状态（recording）- 正在录音
- 思考状态（thinking）- AI分析中
- 庆祝状态（success）- 分析完成
- 错误状态（error）- 处理失败

### 4. 圆形菜单交互
- 点击精灵身体弹出圆形菜单
- 按钮围绕精灵呈圆形排列
- 点击外部区域收起菜单
- 流畅的展开/收起动画

---

## 架构设计

### 后端改造 (voice-server)

#### 1. Agent推理过程回调
**文件**: `voice-server/app/services/agent.py`

添加推理步骤回调机制：
```python
class GrowthAnalysisAgent:
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    async def _step1_extract(self, text: str):
        if self.progress_callback:
            self.progress_callback("STEP 1", "提取活动中...")
        # ... 原有逻辑
        if self.progress_callback:
            self.progress_callback("STEP 1", "✓ 提取完成")
```

#### 2. API路由返回推理步骤
**文件**: `voice-server/app/api/routes.py`

修改 `/process` 端点，返回推理进度：
```python
@app.post("/process")
async def process_audio(file: UploadFile):
    progress_steps = []

    def on_progress(step, message):
        progress_steps.append(f"[{step}] {message}")
        print(f"[{step}] {message}")  # 终端输出

    agent = GrowthAnalysisAgent(progress_callback=on_progress)
    # ...
```

#### 3. 配置项
**文件**: `voice-server/app/config/settings.py`

添加推理过程显示配置：
```yaml
reasoning:
  show_progress: true
  verbose: false  # false=简洁模式, true=详细模式
```

---

### 前端改造 (voice-client)

#### 1. 图片精灵组件
**文件**: `voice-client/sprite_pro.py` (重构)

**核心改动**:
- 移除emoji文字显示
- 使用QPixmap加载PNG图片
- 根据状态切换图片

**新增类**:
```python
class SpriteImageWidget(QWidget):
    def __init__(self):
        self.sprites = {
            'normal': self.load_sprite('normal.png'),
            'recording': self.load_sprite('recording.png'),
            'thinking': self.load_sprite('thinking.png'),
            'success': self.load_sprite('success.png'),
            'error': self.load_sprite('error.png')
        }
        self.current_state = 'normal'

    def set_state(self, state: str):
        self.current_state = state
        self.update()
```

#### 2. 圆形菜单组件
**新增文件**: `voice-client/ui/circular_menu.py`

```python
class CircularMenu(QWidget):
    """圆形弹出菜单"""

    def __init__(self, parent=None):
        self.buttons = []  # 菜单按钮列表
        self.radius = 80   # 菜单半径
        self.animation = None

    def show_menu(self, center_pos: QPoint):
        """在指定位置显示菜单"""
        # 计算按钮位置（圆形分布）
        # 播放展开动画

    def hide_menu(self):
        """隐藏菜单"""
        # 播放收起动画
```

**按钮布局**:
```
        🎤 (录音)
             |
    ⚙️ —— 精灵 —— 🚀 (分析)
             |
        ❓ (帮助)
```

#### 3. 交互逻辑
**文件**: `voice-client/sprite_pro.py`

```python
def mousePressEvent(self, event):
    """点击精灵"""
    if event.button() == Qt.LeftButton:
        if not self.menu_visible:
            self.show_circular_menu()
        else:
            self.hide_circular_menu()

def show_circular_menu(self):
    """显示圆形菜单"""
    self.circular_menu.show_menu(self.sprite.pos())
    self.menu_visible = True

def on_record_clicked(self):
    """点击录音按钮"""
    self.hide_circular_menu()
    self.start_recording()
```

---

## 图片资源设计

### 精灵形象要求
- **风格**: 宝可梦Q版风格
- **尺寸**: 256x256 像素
- **格式**: PNG，透明背景
- **特点**: 可爱、圆润、有亲和力

### 5种状态设计

| 状态 | 描述 | 表情/动作 |
|------|------|-----------|
| normal | 待机 | 微笑，轻轻呼吸 |
| recording | 录音 | 闭眼专注，戴耳机或手持麦克风 |
| thinking | 思考 | 一手托腮，头顶问号 |
| success | 庆祝 | 双手举起，开心表情，星星闪烁 |
| error | 错误 | 垂头丧气，眼泪或晕眩 |

### 图片存储
**目录**: `voice-client/assets/sprites/`
```
voice-client/
└── assets/
    └── sprites/
        ├── normal.png
        ├── recording.png
        ├── thinking.png
        ├── success.png
        └── error.png
```

---

## 技术实现细节

### 图片加载与缓存
```python
def load_sprite(self, filename: str) -> QPixmap:
    """加载并缓存精灵图片"""
    path = Path(__file__).parent / "assets" / "sprites" / filename
    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        raise FileNotFoundError(f"找不到精灵图片: {path}")
    return pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
```

### 圆形菜单绘制
```python
def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.Antialiasing)

    # 绘制半透明背景圆
    painter.setBrush(QColor(0, 0, 0, 100))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(self.center, self.radius, self.radius)

    # 绘制按钮
    for button in self.buttons:
        button.paint(painter)
```

### 动画效果
```python
def animate_show(self):
    """展开动画"""
    self.animation = QPropertyAnimation(self, b"geometry")
    self.animation.setDuration(300)
    self.animation.setEasingCurve(QEasingCurve.OutBack)
    self.animation.start()
```

---

## 数据流

### 完整交互流程

```
1. 用户点击精灵
   ↓
2. 圆形菜单展开（动画）
   ↓
3. 用户点击"🎤 录音"按钮
   ↓
4. 菜单收起，精灵切换到recording状态
   ↓
5. 录音进行中...
   ↓
6. 用户点击停止，或60秒自动停止
   ↓
7. 前端发送音频到后端 /process
   ↓
8. 后端终端输出推理步骤:
   [STEP 1] 提取活动... ✓
   [STEP 2] 分类活动 (2个)... ✓
   [STEP 3] 评估强度... ✓
   ↓
9. 前端接收结果，精灵切换到thinking状态
   ↓
10. 分析完成，精灵切换到success状态
   ↓
11. 显示结果卡片
   ↓
12. 5秒后恢复normal状态
```

---

## 依赖项

### 新增Python依赖
无新增依赖，使用现有PySide6

### 外部资源
- AI图像生成工具（DALL-E 3、Midjourney、Stable Diffusion等）
- 或委托设计师绘制

---

## 测试计划

### 单元测试
- [ ] 图片加载测试
- [ ] 状态切换测试
- [ ] 圆形菜单布局计算测试
- [ ] 动画流畅性测试

### 集成测试
- [ ] 点击精灵 → 菜单显示
- [ ] 点击外部 → 菜单隐藏
- [ ] 点击按钮 → 功能执行
- [ ] 完整录音流程

### UI测试
- [ ] 5种表情切换正常
- [ ] 动画流畅无卡顿
- [ ] 图片资源正确加载
- [ ] 透明背景正确显示

---

## 部署步骤

1. 生成/获取5张精灵图片
2. 创建 `voice-client/assets/sprites/` 目录
3. 放置图片文件
4. 实现后端推理过程输出
5. 实现前端图片精灵组件
6. 实现圆形菜单组件
7. 测试完整流程
8. 提交代码

---

## 风险与备选方案

### 风险1: AI生成的图片质量不理想
**备选方案**: 使用开源精灵资源库，或委托设计师

### 风险2: 圆形菜单在某些分辨率下显示异常
**备选方案**: 添加自适应布局算法

### 风险3: 动画性能问题
**备选方案**: 降低动画帧率或简化效果

---

## 后续优化方向

1. 添加更多表情状态（如：睡觉、打招呼等）
2. 支持自定义精灵皮肤
3. 添加音效（点击、录音、完成等）
4. 支持精灵待机动画（眨眼、呼吸等）
5. 添加3D效果（阴影、高光等）
