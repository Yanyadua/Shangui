# Growth Engine v0.1 设计文档

**项目名称**: Growth Engine - 语音驱动的个人成长量化系统
**版本**: v0.1 (基础功能)
**日期**: 2026-02-20
**状态**: 设计阶段

---

## 1. 项目概述

Growth Engine 是一个语音驱动的个人成长量化系统,通过将每日语音记录转化为结构化活动数据,并量化为"成长增量(delta)",实现个人成长的长期跟踪与分析。

**核心流程**:
```
语音 → 转写 → 活动结构化 → 成长维度增量 → 周期聚合分析
```

**v0.1 目标**: 实现核心数据流,确保每个环节都能正常工作。

---

## 2. 整体架构

### 2.1 架构选择

采用**集中式服务架构**,所有 AI 调用和业务逻辑在服务器端处理:

```
PySide6 客户端                    FastAPI 服务器
     │                                  │
     ├── 录音界面                       ├── Whisper API 转写
     │   └── 录制音频                  ├── DeepSeek Agent (多步骤推理)
     │                                  ├── 规则引擎计算 delta
     └── 上传音频 ──────────────────>  ├── SQLite 存储
                                         └── 返回结果
```

**优点**:
- 架构清晰,职责分明
- API keys 只需在服务器配置一次
- 便于后续添加 Web 界面或其他客户端

---

## 3. 项目结构

```
myVoice/
├── voice-server/              # 后端服务 (Python + FastAPI)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── config/            # 配置管理
│   │   │   ├── __init__.py
│   │   │   └── settings.py    # 加载 config.yaml
│   │   ├── api/               # API 路由
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       └── routes.py  # /api/v1/* 路由
│   │   ├── services/          # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── whisper.py     # Whisper API 调用
│   │   │   ├── deepseek.py    # DeepSeek API 调用
│   │   │   ├── agent.py       # 多步骤推理 Agent
│   │   │   └── calculator.py  # delta 计算规则引擎
│   │   ├── prompts/           # Prompt 模板管理
│   │   │   ├── __init__.py
│   │   │   ├── manager.py     # Prompt 管理器
│   │   │   └── templates/     # Jinja2 模板
│   │   │       ├── system_prompt.j2
│   │   │       ├── extract_activities.j2
│   │   │       ├── classify_activity.j2
│   │   │       └── evaluate_metrics.j2
│   │   ├── models/            # 数据模型
│   │   │   ├── __init__.py
│   │   │   └── schemas.py     # Pydantic 模型
│   │   └── db/                # 数据库
│   │       ├── __init__.py
│   │       └── database.py    # SQLite 连接和表定义
│   ├── config.yaml            # 配置文件
│   ├── requirements.txt
│   └── run.py                 # 服务器启动脚本
│
├── voice-client/              # PySide6 桌面客户端
│   ├── main.py                # 应用入口
│   ├── ui/                    # UI 组件
│   │   ├── __init__.py
│   │   └── main_window.py     # 主窗口(录音界面)
│   ├── services/              # 客户端服务
│   │   ├── __init__.py
│   │   └── api_client.py      # 与服务器通信
│   ├── requirements.txt
│   └── resources/             # 资源文件
│
└── docs/                      # 文档
    └── plans/                 # 设计和实现计划
```

---

## 4. 核心数据模型

### 4.1 活动类型(固定枚举)

1. **Learning Input** - 被动学习、阅读、观看教程
2. **Active Practice** - 刻意练习、刷题、实验性编码
3. **Problem Solving** - 解决bug、调试、故障排查
4. **Production Output** - 写代码、写文档、做项目
5. **System Improvement** - 重构、优化、学习新工具
6. **Energy Management** - 休息、运动、冥想、睡眠管理

### 4.2 成长维度(固定 5 维)

1. `knowledge_intake` - 知识摄入
2. `skill_fluency` - 技能熟练度
3. `complexity_handling` - 复杂度处理
4. `system_thinking` - 系统思维
5. `execution` - 执行力

### 4.3 DailyRecord 数据结构

```json
{
  "date": "2026-02-20",
  "raw_text": "今天刷了两小时LeetCode,调试了一个并发问题...",
  "activities": [
    {
      "type": "Active Practice",
      "topic": "LeetCode",
      "description": "刷算法题",
      "intensity": 0.8,
      "duration_estimate": 2.0
    }
  ],
  "delta": {
    "knowledge_intake": 0.1,
    "skill_fluency": 0.15,
    "complexity_handling": 0.2,
    "system_thinking": 0.05,
    "execution": 0.1
  }
}
```

---

## 5. Agent 多步骤推理工作流

### 5.1 工作流架构

```
输入: 转写后的文本
    ↓
┌─────────────────────────────────────┐
│ Step 1: 提取活动列表                 │
│ - 识别所有提及的活动                 │
│ - 初步分类和估计时长                 │
│ - Prompt: extract_activities.j2     │
└─────────────────────────────────────┘
    ↓ activities[]
┌─────────────────────────────────────┐
│ Step 2: 精确分类每个活动             │
│ - 对每个活动确认类型                 │
│ - 提取主题关键词                     │
│ - Prompt: classify_activity.j2      │
│ (并行处理所有活动)                   │
└─────────────────────────────────────┘
    ↓ classified_activities[]
┌─────────────────────────────────────┐
│ Step 3: 评估活动强度                 │
│ - 对每个活动评估 intensity           │
│ - 基于认知负荷和专注度               │
│ - Prompt: evaluate_metrics.j2       │
│ (并行处理所有活动)                   │
└─────────────────────────────────────┘
    ↓ final_activities[]
    ↓
┌─────────────────────────────────────┐
│ Step 4: 规则引擎计算                 │
│ - 使用权重配置计算 delta             │
│ - 应用单维度上限(0.3)                │
│ - 汇总5个维度的增量                  │
└─────────────────────────────────────┘
    ↓
输出: { activities, delta }
```

### 5.2 Prompt 模板设计

使用 **Jinja2 模板引擎**管理所有 prompt,支持版本管理和快速调整。

#### system_prompt.j2
定义 Agent 角色、活动类型、评估标准和输出要求。

#### extract_activities.j2
从用户文本中提取所有活动列表。

#### classify_activity.j2
对单个活动进行精确分类。

#### evaluate_metrics.j2
评估单个活动的 intensity(强度)。

### 5.3 成本估算

假设每天 3 个活动:
- Step 1: 1 次调用(长文本)
- Step 2: 3 次并行调用(短文本)
- Step 3: 3 次并行调用(短文本)
- **总计**: 7 次 LLM 调用/天

---

## 6. 规则引擎设计

### 6.1 delta 计算公式

```
delta = base_weight × intensity × log(duration + 1)
```

使用自然对数 `log`。

每日单维度最大 delta 上限为 `0.3`。

### 6.2 权重配置

```yaml
weights:
  Learning Input:
    knowledge_intake: 0.15
    execution: 0.05

  Active Practice:
    skill_fluency: 0.15
    execution: 0.1

  Problem Solving:
    complexity_handling: 0.18
    execution: 0.08

  System Improvement:
    system_thinking: 0.2
    complexity_handling: 0.1

  Production Output:
    execution: 0.15
    skill_fluency: 0.1

  Energy Management:
    execution: 0.05
```

---

## 7. API 设计

### 7.1 POST /api/v1/process

**一条龙服务**: 转写 + 解析 + 计算

**输入**:
```
Content-Type: multipart/form-data
Body: audio_file (upload)
```

**输出**:
```json
{
  "text": "转写文本...",
  "activities": [...],
  "delta": {
    "knowledge_intake": 0.1,
    "skill_fluency": 0.15,
    "complexity_handling": 0.2,
    "system_thinking": 0.05,
    "execution": 0.1
  },
  "date": "2026-02-20"
}
```

### 7.2 GET /api/v1/records

查询历史记录

**参数**: `?date=2026-02-20`

### 7.3 GET /api/v1/health

数据库健康检查

---

## 8. 数据库设计

### 8.1 daily_records 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| date | DATE | 日期 |
| raw_text | TEXT | 原始转写文本 |
| activities_json | TEXT | 活动 JSON 数组 |
| delta_knowledge | FLOAT | knowledge_intake 增量 |
| delta_skill | FLOAT | skill_fluency 增量 |
| delta_complexity | FLOAT | complexity_handling 增量 |
| delta_system | FLOAT | system_thinking 增量 |
| delta_execution | FLOAT | execution 增量 |
| created_at | TIMESTAMP | 创建时间 |

---

## 9. 配置文件设计

### config.yaml

```yaml
# API Keys
api_keys:
  deepseek: "YOUR_DEEPSEEK_API_KEY"
  whisper: "YOUR_WHISPER_API_KEY"

# 服务配置
server:
  host: "127.0.0.1"
  port: 8000
  cors_origins:
    - "http://localhost:5173"

# 数据库
database:
  path: "data/growth_engine.db"

# 规则引擎权重
weights:
  Learning Input:
    knowledge_intake: 0.15
    execution: 0.05
  Active Practice:
    skill_fluency: 0.15
    execution: 0.1
  Problem Solving:
    complexity_handling: 0.18
    execution: 0.08
  System Improvement:
    system_thinking: 0.2
    complexity_handling: 0.1
  Production Output:
    execution: 0.15
    skill_fluency: 0.1
  Energy Management:
    execution: 0.05

# 计算参数
calculation:
  max_delta_per_dimension: 0.3
```

---

## 10. 技术栈

### 后端 (voice-server)
- Python 3.10+
- FastAPI
- SQLite
- httpx (HTTP 客户端)
- Pydantic (数据验证)
- Jinja2 (Prompt 模板)

### 前端 (voice-client)
- PySide6 (Qt6 Python 绑定)
- pyaudio (录音)

### AI 服务
- OpenAI Whisper API (语音转写)
- DeepSeek Chat API (活动解析)

---

## 11. 验收标准

v0.1 完成标准:
- [ ] 客户端可以录音并上传音频
- [ ] 服务器调用 Whisper API 成功转写
- [ ] Agent 正确输出结构化 activities JSON
- [ ] 规则引擎正确计算 delta (5个维度)
- [ ] DailyRecord 成功持久化到 SQLite
- [ ] API 可以查询历史记录

---

## 12. 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| LLM 输出不稳定 | 使用多步骤推理,增加结构化验证 |
| Prompt 效果不佳 | 使用 Jinja2 模板,支持快速迭代调整 |
| 并行调用成本高 | v0.2 考虑批处理模式 |
| API 密钥泄露 | 使用 config.yaml,加入 .gitignore |

---

## 13. 设计哲学

- **活动是语义层, delta 是数学层**
- **成长是动量,不是评分**
- **结构优先于功能堆砌**
- **可计算优先于可展示**
