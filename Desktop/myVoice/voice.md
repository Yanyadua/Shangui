# 产品需求文档（PRD）

# 项目名称
Growth Engine —— 语音驱动的个人成长量化系统

# 版本
v1.0（开发版）

# 作者
[填写你的名字]

# 日期
2026-02-XX

---

# 一、项目背景

当前个人学习与工作复盘主要依赖文本笔记或主观总结，缺乏结构化、量化与长期趋势分析能力。  
随着语音识别与大模型能力成熟，可以将每日语音记录转化为结构化活动数据，并进一步量化为“成长增量（delta）”。

本项目目标是构建一个：

语音 → 活动结构化 → 成长维度增量 → 周期聚合分析

的成长动力学系统。

该系统为单用户使用，优先保证模型稳定性与数据可计算性。

---

# 二、项目目标

## 2.1 功能目标

- 支持每日语音录入
- 调用 DeepSeek API 进行活动解析
- 通过规则引擎计算成长维度 delta
- 存储每日记录
- 支持周报与月报生成
- 支持权重调整与历史重算

## 2.2 非目标

- 不做多用户
- 不做复杂可视化
- 不做能力等级评分
- 不做 gamification
- 不做公开分享

---

# 三、系统架构

## 3.1 总体架构

桌面精灵（录音 UI）
        ↓
轻量服务器（FastAPI）
        ↓
1. Whisper 转写
2. DeepSeek 解析活动
3. 规则引擎计算 delta
4. SQLite 存储
5. 报告生成

## 3.2 技术选型

服务器：
- Python 3.10+
- FastAPI
- SQLite
- requests / httpx（调用 DeepSeek API）

桌面端：
- PySide6（推荐）
- 或 Tauri（可选）

转写：
- Whisper 本地模型 或 远程 API

大模型：
- DeepSeek Chat API

---

# 四、核心数据模型

## 4.1 活动类型（固定枚举）

1. Learning Input
2. Active Practice
3. Problem Solving
4. Production Output
5. System Improvement
6. Energy Management

---

## 4.2 成长维度（固定 5 维）

1. knowledge_intake
2. skill_fluency
3. complexity_handling
4. system_thinking
5. execution

---

## 4.3 DailyRecord 数据结构

```json
{
  "date": "2026-02-19",
  "raw_text": "...",
  "activities": [],
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

# 五、DeepSeek API 设计

## 5.1 DeepSeek 调用方式

使用 Chat Completion API：

POST https://api.deepseek.com/chat/completions

Headers:
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

---

## 5.2 Prompt 设计（核心）

系统 Prompt：

你是一个成长记录结构化分析助手。
请根据用户文本，识别出活动列表。
活动类型必须属于以下枚举：
- Learning Input
- Active Practice
- Problem Solving
- Production Output
- System Improvement
- Energy Management

每个活动必须包含：
- type
- topic
- intensity（0~1 之间）
- duration_estimate（小时数）

只输出 JSON，不要输出解释文字。

---

## 5.3 请求示例

```json
{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "system",
      "content": "你是一个成长记录结构化分析助手..."
    },
    {
      "role": "user",
      "content": "今天刷了两小时LeetCode，调试了一个并发问题..."
    }
  ],
  "temperature": 0.2
}
```

---

## 5.4 期望输出格式

```json
{
  "activities": [
    {
      "type": "Active Practice",
      "topic": "LeetCode",
      "intensity": 0.8,
      "duration_estimate": 2.0
    },
    {
      "type": "Problem Solving",
      "topic": "Concurrency Debug",
      "intensity": 0.9,
      "duration_estimate": 1.5
    }
  ]
}
```

---

# 六、规则引擎设计

## 6.1 delta 计算公式

```
delta = base_weight × intensity × log(duration + 1)
```

使用自然对数 log。

每日单维度最大 delta 上限为 0.3。

---

## 6.2 权重配置文件（YAML 示例）

```yaml
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

# 七、数据库设计

## 7.1 daily_records 表

字段：

- id (UUID)
- date (DATE)
- raw_text (TEXT)
- activities_json (TEXT)
- delta_knowledge (FLOAT)
- delta_skill (FLOAT)
- delta_complexity (FLOAT)
- delta_system (FLOAT)
- delta_execution (FLOAT)
- created_at (TIMESTAMP)

---

# 八、API 设计

## 8.1 POST /api/v1/transcribe

输入：
audio file

输出：
```json
{ "text": "..." }
```

---

## 8.2 POST /api/v1/parse

输入：
```json
{ "text": "..." }
```

输出：
```json
{ "activities": [...] }
```

---

## 8.3 POST /api/v1/calculate

输入：
```json
{ "activities": [...] }
```

输出：
```json
{ "delta": {...} }
```

---

## 8.4 GET /api/v1/report/weekly

输出：
Markdown 字符串

---

# 九、周报生成逻辑

周报内容包含：

1. 各维度累计 delta
2. 活动类型分布
3. 高频主题
4. 单日最高成长日
5. 总成长值

报告输出为 Markdown。

---

# 十、验收标准

- DeepSeek 正确输出 JSON 结构
- 规则引擎可正确计算 delta
- daily record 可持久化
- 周报可正常生成
- 权重修改后可重算历史记录

---

# 十一、风险控制

风险：
- LLM 输出不稳定
- 时长估计误差
- 权重设计不合理

解决：
- 限制 JSON 输出
- 允许用户校正活动
- 权重配置化
- 保存原始活动用于回放重算

---

# 十二、里程碑

v0.1：
- 语音 → 解析 → delta → 存储

v0.2：
- 周报生成
- 权重可调

v1.0：
- 稳定性优化
- 长期趋势分析

---

# 设计哲学

- 活动是语义层
- delta 是数学层
- 成长是动量，不是评分
- 结构优先于功能堆砌
- 可计算优先于可展示