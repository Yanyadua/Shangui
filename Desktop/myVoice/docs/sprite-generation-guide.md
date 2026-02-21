# 精灵图片生成指南

本文档提供生成Growth Engine桌面精灵图片的详细指南。

## 📐 图片要求

- **尺寸**: 256x256 或 512x512 像素
- **格式**: PNG，必须透明背景
- **风格**: 宝可梦Q版风格，可爱圆润
- **颜色**: 每个状态不同配色方案

## 🎨 5种状态设计

### 1. Normal (待机状态)
**配色**: 绿色 (#81c784)
**表情**: 微笑友好
**描述**:
```
A cute chibi Pokémon-style mascot character for a productivity app,
smiling friendly, simple round design, green color scheme,
white background, 256x256 PNG with transparent background,
adorable and approachable
```

### 2. Recording (录音状态)
**配色**: 红色 (#ef5350)
**表情**: 专注，闭眼或睁大眼睛
**道具**: 手持麦克风或戴耳机
**描述**:
```
A cute chibi Pokémon-style mascot character recording audio,
focused expression with closed eyes or wide open, holding a microphone,
red color scheme, white background, 256x256 PNG with transparent background
```

### 3. Thinking (思考状态)
**配色**: 蓝色 (#64b5f6)
**表情**: 思考状
**道具**: 手托下巴，头顶有小问号
**描述**:
```
A cute chibi Pokémon-style mascot character thinking deeply,
hand on chin, small question mark floating above head,
blue color scheme, white background, 256x256 PNG with transparent background
```

### 4. Success (庆祝状态)
**配色**: 黄色/金色 (#ffd54f)
**表情**: 开心大笑
**道具**: 双手举起，周围有星星和闪光
**描述**:
```
A cute chibi Pokémon-style mascot character celebrating,
arms raised in victory, big happy smile, stars and sparkles around,
yellow/gold color scheme, white background, 256x256 PNG with transparent background
```

### 5. Error (错误状态)
**配色**: 灰色 (#90a4ae)
**表情**: 难过或晕眩
**道具**: 眼泪或晕眩螺旋眼
**描述**:
```
A cute chibi Pokémon-style mascot character looking sad,
tear drop, dizzy spiral eyes, gray color scheme,
white background, 256x256 PNG with transparent background
```

## 🛠️ 推荐工具

### DALL-E 3 (推荐)
**优点**:
- 理解自然语言能力强
- 支持透明背景
- 质量稳定

**使用方法**:
1. 访问 https://openai.com/dall-e-3
2. 复制上面的提示词
3. 生成并下载图片
4. 确保保存为PNG格式

### Midjourney
**优点**:
- 艺术质量高
- 风格多样

**提示词格式**:
```
chibi Pokémon-style mascot, [状态描述], green color scheme,
white background, transparent background --style raw --ar 1:1
```

### Stable Diffusion
**优点**:
- 完全免费
- 本地运行
- 可控性强

**推荐模型**:
- Anything V5
- CounterfeitV3
- GhostMix

**关键词**:
```
chibi, pokemon style, cute mascot, [表情], [颜色],
simple design, white background, transparent background
```

## 📁 图片放置

生成图片后，保存到以下位置：

```
voice-client/assets/sprites/
├── normal.png      # 待机状态
├── recording.png   # 录音状态
├── thinking.png    # 思考状态
├── success.png     # 庆祝状态
└── error.png       # 错误状态
```

## ✅ 验证图片

保存图片后，运行以下命令验证：

```bash
cd voice-client/assets/sprites
ls -lh *.png
file *.png
```

期望输出：
```
-rw-r--r-- 1 user staff  45K Feb 21 14:30 normal.png
-rw-r--r-- 1 user staff  52K Feb 21 14:31 recording.png
...
normal.png: PNG image data, 256 x 256, 8-bit/color RGBA
...
```

注意 `RGBA` 表示有透明通道。

## 🔄 替换图片

替换图片后，重启精灵即可看到新图片：

```bash
# 停止旧精灵
pkill -f sprite_pro.py

# 启动新精灵
./start_sprite.sh
```

## 💡 提示

1. **一致性**: 确保所有5张图片的角色形象一致
2. **简洁**: 避免过多细节，小尺寸显示更清晰
3. **对比度**: 使用明亮颜色，在深色背景下也清晰
4. **居中**: 角色应该居中，周围留出适当空白

## 🆘 故障排除

### 问题：图片不显示
**解决**:
1. 检查文件名是否正确
2. 检查文件大小（不是0字节）
3. 检查格式（PNG with RGBA）

### 问题：背景不透明
**解决**:
1. DALL-E 3: 添加 "transparent background"
2. Midjourney: 使用背景移除工具
3. Photoshop/GIMP: 使用魔棒工具删除背景

### 问题：角色不一致
**解决**:
1. 使用相同的种子值
2. 在提示词中强调 "same character"
3. 手动编辑调整

## 📚 参考资料

- [DALL-E 3 文档](https://platform.openai.com/docs/guides/images)
- [Midjourney 提示词指南](https://docs.midjourney.com/docs/prompts)
- [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
