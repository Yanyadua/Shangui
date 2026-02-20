# Growth Engine v0.1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建 Growth Engine v0.1 基础功能 - 实现语音录音到成长增量计算的完整数据流

**Architecture:** 采用集中式服务架构,PySide6 客户端负责录音和上传,FastAPI 服务器处理 Whisper 转写、DeepSeek 多步骤推理 Agent 解析活动、规则引擎计算 delta 并存储到 SQLite

**Tech Stack:** Python 3.10+, FastAPI, PySide6, SQLite, httpx, Pydantic, Jinja2, OpenAI Whisper API, DeepSeek Chat API

---

## Task 1: 项目初始化与目录结构

**Files:**
- Create: `voice-server/requirements.txt`
- Create: `voice-server/config.yaml`
- Create: `voice-server/run.py`
- Create: `voice-client/requirements.txt`
- Create: `voice-client/main.py`
- Create: `.gitignore`

**Step 1: 创建项目目录结构**

```bash
cd /Users/yaoduanyang/Desktop/myVoice
mkdir -p voice-server/app/{config,api/v1,services,prompts/templates,models,db}
mkdir -p voice-client/{ui,services,resources}
mkdir -p data
```

**Step 2: 创建 voice-server/requirements.txt**

```txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.10.0
pydantic-settings==2.6.0
httpx==0.28.0
python-multipart==0.0.17
jinja2==3.1.4
pyyaml==6.0.2
aiosqlite==0.20.0
python-dotenv==1.0.1
```

**Step 3: 创建 voice-server/config.yaml**

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

**Step 4: 创建 voice-server/run.py**

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
```

**Step 5: 创建 voice-client/requirements.txt**

```txt
PySide6==6.8.0
pyaudio==0.2.14
requests==2.32.3
python-dotenv==1.0.1
```

**Step 6: 创建 voice-client/main.py**

```python
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

**Step 7: 创建 .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Config
voice-server/config.yaml
.env

# Database
data/*.db
data/*.db-journal

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store

# Audio uploads
voice-server/uploads/
```

**Step 8: 提交**

```bash
git add .
git commit -m "feat: initialize project structure and dependencies"
```

---

## Task 2: 配置管理模块

**Files:**
- Create: `voice-server/app/__init__.py`
- Create: `voice-server/app/config/__init__.py`
- Create: `voice-server/app/config/settings.py`

**Step 1: 创建 voice-server/app/config/__init__.py**

```python
from .settings import settings, get_config

__all__ = ["settings", "get_config"]
```

**Step 2: 创建 voice-server/app/config/settings.py**

```python
from pathlib import Path
from typing import Dict, Any
import yaml
from pydantic import BaseModel, Field


class APIKeys(BaseModel):
    deepseek: str
    whisper: str


class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = []


class DatabaseConfig(BaseModel):
    path: str = "data/growth_engine.db"


class CalculationConfig(BaseModel):
    max_delta_per_dimension: float = 0.3


class Settings(BaseModel):
    api_keys: APIKeys
    server: ServerConfig
    database: DatabaseConfig
    weights: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    calculation: CalculationConfig = Field(default_factory=CalculationConfig)

    class Config:
        extra = "ignore"


def load_config(config_path: str = None) -> Settings:
    """从 YAML 文件加载配置"""
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config.yaml"

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    return Settings(**config_data)


# 全局配置实例
settings = load_config()

def get_config() -> Settings:
    return settings
```

**Step 3: 提交**

```bash
git add voice-server/app/config/
git commit -m "feat: add configuration management module"
```

---

## Task 3: 数据模型定义

**Files:**
- Create: `voice-server/app/models/__init__.py`
- Create: `voice-server/app/models/schemas.py`

**Step 1: 创建 voice-server/app/models/__init__.py**

```python
from .schemas import (
    Activity,
    Delta,
    DailyRecord,
    DailyRecordCreate,
    ProcessRequest,
    ProcessResponse
)

__all__ = [
    "Activity",
    "Delta",
    "DailyRecord",
    "DailyRecordCreate",
    "ProcessRequest",
    "ProcessResponse"
]
```

**Step 2: 创建 voice-server/app/models/schemas.py**

```python
from datetime import date, datetime
from typing import List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ActivityType(str, Enum):
    """活动类型枚举"""
    LEARNING_INPUT = "Learning Input"
    ACTIVE_PRACTICE = "Active Practice"
    PROBLEM_SOLVING = "Problem Solving"
    PRODUCTION_OUTPUT = "Production Output"
    SYSTEM_IMPROVEMENT = "System Improvement"
    ENERGY_MANAGEMENT = "Energy Management"


class Activity(BaseModel):
    """活动模型"""
    type: ActivityType
    topic: str = Field(..., description="活动主题")
    description: str = Field(default="", description="活动详细描述")
    intensity: float = Field(..., ge=0, le=1, description="活动强度 0-1")
    duration_estimate: float = Field(..., gt=0, description="估计时长(小时)")

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v):
        """标准化活动类型"""
        if isinstance(v, str):
            # 处理可能的格式变化
            type_map = {
                "learning_input": "Learning Input",
                "active_practice": "Active Practice",
                "problem_solving": "Problem Solving",
                "production_output": "Production Output",
                "system_improvement": "System Improvement",
                "energy_management": "Energy Management",
            }
            return type_map.get(v.lower().replace(" ", "_"), v)
        return v


class Delta(BaseModel):
    """成长增量模型"""
    knowledge_intake: float = Field(default=0.0, ge=0)
    skill_fluency: float = Field(default=0.0, ge=0)
    complexity_handling: float = Field(default=0.0, ge=0)
    system_thinking: float = Field(default=0.0, ge=0)
    execution: float = Field(default=0.0, ge=0)


class DailyRecordCreate(BaseModel):
    """创建每日记录请求"""
    date: date
    raw_text: str
    activities: List[Activity]
    delta: Delta


class DailyRecord(DailyRecordCreate):
    """每日记录响应"""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProcessResponse(BaseModel):
    """处理音频响应"""
    text: str
    activities: List[Activity]
    delta: Delta
    date: date
```

**Step 3: 提交**

```bash
git add voice-server/app/models/
git commit -m "feat: add data models with Pydantic"
```

---

## Task 4: Prompt 模板管理

**Files:**
- Create: `voice-server/app/prompts/__init__.py`
- Create: `voice-server/app/prompts/manager.py`
- Create: `voice-server/app/prompts/templates/system_prompt.j2`
- Create: `voice-server/app/prompts/templates/extract_activities.j2`
- Create: `voice-server/app/prompts/templates/classify_activity.j2`
- Create: `voice-server/app/prompts/templates/evaluate_metrics.j2`

**Step 1: 创建 voice-server/app/prompts/__init__.py**

```python
from .manager import PromptManager, get_prompt_manager

__all__ = ["PromptManager", "get_prompt_manager"]
```

**Step 2: 创建 voice-server/app/prompts/manager.py**

```python
from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
from typing import Dict

class PromptManager:
    """Prompt 模板管理器"""

    def __init__(self, templates_dir: str = None):
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "templates"
        self.templates_dir = Path(templates_dir)
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self._cache: Dict[str, Template] = {}

    def get_template(self, name: str) -> Template:
        """获取并缓存模板"""
        if name not in self._cache:
            self._cache[name] = self.env.get_template(name)
        return self._cache[name]

    def render(self, template_name: str, **context) -> str:
        """渲染模板"""
        template = self.get_template(template_name)
        return template.render(**context)

    # 便捷方法
    def get_system_prompt(self) -> str:
        return self.render("system_prompt.j2")

    def get_extract_prompt(self, user_text: str) -> str:
        return self.render("extract_activities.j2", user_text=user_text)

    def get_classify_prompt(self, activity_description: str, duration: float) -> str:
        return self.render(
            "classify_activity.j2",
            activity_description=activity_description,
            duration_estimate=duration
        )

    def get_evaluate_prompt(self, activity_type: str, topic: str, description: str) -> str:
        return self.render(
            "evaluate_metrics.j2",
            activity_type=activity_type,
            activity_topic=topic,
            activity_description=description
        )


# 全局实例
_prompt_manager: PromptManager = None


def get_prompt_manager() -> PromptManager:
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager
```

**Step 3: 创建 voice-server/app/prompts/templates/system_prompt.j2**

```jinja2
你是一个个人成长记录结构化分析助手,专门帮助用户将日常语音记录转化为可量化的成长数据。

你的任务是:
1. 识别用户文本中的所有活动
2. 将每个活动归类到6种活动类型之一
3. 评估活动的强度(intensity)和时长(duration)

## 活动类型定义:
- **Learning Input**: 被动学习、阅读、观看教程、听课等知识输入行为
- **Active Practice**: 刻意练习、刷题、实验性编码、技能训练等主动练习
- **Problem Solving**: 解决bug、调试、排查问题、故障排查等解决问题行为
- **Production Output**: 写代码、写文档、做项目、产出作品等创造性输出
- **System Improvement**: 重构、优化、学习新工具、改进工作流程等系统提升
- **Energy Management**: 休息、运动、冥想、睡眠管理等能量管理活动

## 评估标准:
- **intensity** (0~1): 活动的专注度和认知负荷
  - 0.1-0.3: 低强度(随意浏览、简单复习)
  - 0.4-0.6: 中等强度(正常学习、常规工作)
  - 0.7-0.9: 高强度(深度思考、解决复杂问题)
  - 1.0: 极高强度(突破性工作、极度专注)

- **duration_estimate**: 以小时为单位的活动时长

## 输出要求:
- 只输出纯 JSON 格式
- 不要包含任何解释文字
- 确保每个活动都包含所有必需字段
```

**Step 4: 创建 voice-server/app/prompts/templates/extract_activities.j2**

```jinja2
基于以下用户文本,提取所有活动:

用户文本:
```
{{ user_text }}
```

请输出包含所有活动的 JSON 数组,每个活动包含:
- type: 活动类型(必须是6种类型之一)
- topic: 活动主题(简短描述)
- description: 活动详细描述
- duration_estimate: 估计时长(小时)

输出格式:
```json
{
  "activities": [
    {
      "type": "Activity Type",
      "topic": "Topic name",
      "description": "Detailed description",
      "duration_estimate": 2.0
    }
  ]
}
```
```

**Step 5: 创建 voice-server/app/prompts/templates/classify_activity.j2**

```jinja2
对以下活动进行分类和评估:

活动描述: {{ activity_description }}
估计时长: {{ duration_estimate }} 小时

请输出:
```json
{
  "type": "确定的Activity Type(6种之一)",
  "topic": "简短主题",
  "intensity": 0.8,
  "duration_estimate": {{ duration_estimate }}
}
```

注意:
- type 必须严格匹配6种活动类型
- intensity 基于活动的认知负荷和专注度
```

**Step 6: 创建 voice-server/app/prompts/templates/evaluate_metrics.j2**

```jinja2
评估以下活动的强度(intensity):

活动类型: {{ activity_type }}
活动主题: {{ activity_topic }}
活动描述: {{ activity_description }}

请评估并输出:
```json
{
  "intensity": 0.75,
  "reasoning": "简要说明评估理由"
}
```

intensity 评估标准:
- 0.1-0.3: 低强度 - 机械性任务、轻松复习
- 0.4-0.6: 中强度 - 常规学习工作
- 0.7-0.9: 高强度 - 深度思考、复杂问题
- 1.0: 极高强度 - 突破性工作
```

**Step 7: 提交**

```bash
git add voice-server/app/prompts/
git commit -m "feat: add prompt template manager with Jinja2"
```

---

## Task 5: DeepSeek 客户端

**Files:**
- Create: `voice-server/app/services/__init__.py`
- Create: `voice-server/app/services/deepseek.py`

**Step 1: 创建 voice-server/app/services/__init__.py**

```python
from .whisper import WhisperClient
from .deepseek import DeepSeekClient
from .agent import GrowthAnalysisAgent
from .calculator import DeltaCalculator

__all__ = [
    "WhisperClient",
    "DeepSeekClient",
    "GrowthAnalysisAgent",
    "DeltaCalculator"
]
```

**Step 2: 创建 voice-server/app/services/deepseek.py**

```python
import httpx
import json
import asyncio
from typing import Dict, Optional
from app.config.settings import get_config


class DeepSeekClient:
    """DeepSeek API 客户端"""

    def __init__(self):
        config = get_config()
        self.api_key = config.api_keys.deepseek
        self.base_url = "https://api.deepseek.com"
        self.model = "deepseek-chat"

    async def chat(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2
    ) -> str:
        """发送聊天请求并返回响应文本"""

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def chat_with_json(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict:
        """发送聊天请求并解析 JSON 响应"""

        response_text = await self.chat(user_prompt, system_prompt)

        # 提取 JSON 代码块
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        return json.loads(response_text)
```

**Step 3: 提交**

```bash
git add voice-server/app/services/deepseek.py
git commit -m "feat: add DeepSeek API client"
```

---

## Task 6: Whisper 客户端

**Files:**
- Create: `voice-server/app/services/whisper.py`

**Step 1: 创建 voice-server/app/services/whisper.py**

```python
import httpx
from pathlib import Path
from typing import Optional
from app.config.settings import get_config


class WhisperClient:
    """Whisper API 客户端 (使用 OpenAI Whisper API)"""

    def __init__(self):
        config = get_config()
        self.api_key = config.api_keys.whisper
        self.base_url = "https://api.openai.com/v1"

    async def transcribe(
        self,
        audio_file_path: str,
        language: str = "zh"
    ) -> str:
        """转写音频文件为文本"""

        audio_path = Path(audio_file_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(audio_path, "rb") as audio_file:
                files = {
                    "file": (audio_path.name, audio_file, "audio/mpeg")
                }
                data = {
                    "model": "whisper-1",
                    "language": language
                }

                response = await client.post(
                    f"{self.base_url}/audio/transcriptions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    files=files,
                    data=data
                )
                response.raise_for_status()
                result = response.json()
                return result["text"]
```

**Step 2: 提交**

```bash
git add voice-server/app/services/whisper.py
git commit -m "feat: add Whisper API client"
```

---

## Task 7: Agent 多步骤推理

**Files:**
- Create: `voice-server/app/services/agent.py`

**Step 1: 创建 voice-server/app/services/agent.py**

```python
import asyncio
import json
from typing import List, Dict
from .deepseek import DeepSeekClient
from ..prompts.manager import get_prompt_manager
from ..models.schemas import Activity


class GrowthAnalysisAgent:
    """成长分析 Agent - 多步骤推理"""

    def __init__(self, deepseek_client: DeepSeekClient = None):
        self.deepseek = deepseek_client or DeepSeekClient()
        self.prompts = get_prompt_manager()

    async def analyze(self, transcribed_text: str) -> List[Activity]:
        """执行完整的分析流程"""

        # Step 1: 提取活动列表
        activities = await self._step1_extract(transcribed_text)

        # Step 2: 并行分类所有活动
        classified = await self._step2_classify(activities)

        # Step 3: 并行评估所有活动强度
        final_activities = await self._step3_evaluate(classified)

        # 转换为 Pydantic 模型
        return [Activity(**act) for act in final_activities]

    async def _step1_extract(self, text: str) -> List[Dict]:
        """提取初始活动列表"""
        prompt = self.prompts.get_extract_prompt(text)
        response = await self.deepseek.chat_with_json(
            user_prompt=prompt,
            system_prompt=self.prompts.get_system_prompt()
        )
        return response.get("activities", [])

    async def _step2_classify(self, activities: List[Dict]) -> List[Dict]:
        """并行分类所有活动"""
        tasks = [
            self._classify_single_activity(activity)
            for activity in activities
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 过滤异常结果
        valid_results = [r for r in results if not isinstance(r, Exception)]
        return valid_results

    async def _classify_single_activity(self, activity: Dict) -> Dict:
        """分类单个活动"""
        prompt = self.prompts.get_classify_prompt(
            activity.get("description", ""),
            activity.get("duration_estimate", 1.0)
        )
        response = await self.deepseek.chat_with_json(
            user_prompt=prompt,
            system_prompt=self.prompts.get_system_prompt()
        )
        return response

    async def _step3_evaluate(self, classified_activities: List[Dict]) -> List[Dict]:
        """并行评估所有活动强度"""
        tasks = [
            self._evaluate_single_activity(activity)
            for activity in classified_activities
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 过滤异常结果
        valid_results = [r for r in results if not isinstance(r, Exception)]
        return valid_results

    async def _evaluate_single_activity(self, activity: Dict) -> Dict:
        """评估单个活动强度"""
        prompt = self.prompts.get_evaluate_prompt(
            activity.get("type", ""),
            activity.get("topic", ""),
            activity.get("description", "")
        )
        response = await self.deepseek.chat_with_json(
            user_prompt=prompt,
            system_prompt=self.prompts.get_system_prompt()
        )

        # 合并 intensity 到原有活动数据
        activity["intensity"] = response.get("intensity", 0.5)
        return activity
```

**Step 2: 提交**

```bash
git add voice-server/app/services/agent.py
git commit -m "feat: add multi-step reasoning agent"
```

---

## Task 8: Delta 计算规则引擎

**Files:**
- Create: `voice-server/app/services/calculator.py`

**Step 1: 创建 voice-server/app/services/calculator.py**

```python
import math
from typing import List, Dict
from ..models.schemas import Activity, Delta
from ..config.settings import get_config


class DeltaCalculator:
    """Delta 计算规则引擎"""

    # 活动类型到维度的权重映射
    ACTIVITY_WEIGHTS = {
        "Learning Input": {
            "knowledge_intake": 0.15,
            "execution": 0.05
        },
        "Active Practice": {
            "skill_fluency": 0.15,
            "execution": 0.1
        },
        "Problem Solving": {
            "complexity_handling": 0.18,
            "execution": 0.08
        },
        "System Improvement": {
            "system_thinking": 0.2,
            "complexity_handling": 0.1
        },
        "Production Output": {
            "execution": 0.15,
            "skill_fluency": 0.1
        },
        "Energy Management": {
            "execution": 0.05
        }
    }

    def __init__(self):
        config = get_config()
        self.max_delta = config.calculation.max_delta_per_dimension
        # 使用配置文件中的权重覆盖默认权重
        if config.weights:
            self.ACTIVITY_WEIGHTS = config.weights

    def calculate(self, activities: List[Activity]) -> Delta:
        """计算所有活动的总 delta"""

        # 初始化各维度增量
        deltas = {
            "knowledge_intake": 0.0,
            "skill_fluency": 0.0,
            "complexity_handling": 0.0,
            "system_thinking": 0.0,
            "execution": 0.0
        }

        # 累加每个活动的 delta
        for activity in activities:
            activity_deltas = self._calculate_activity_delta(activity)
            for dimension, value in activity_deltas.items():
                deltas[dimension] += value

        # 应用单维度上限
        for dimension in deltas:
            deltas[dimension] = min(deltas[dimension], self.max_delta)

        return Delta(**deltas)

    def _calculate_activity_delta(self, activity: Activity) -> Dict[str, float]:
        """计算单个活动的 delta"""

        activity_type = activity.type.value if hasattr(activity.type, 'value') else activity.type
        weights = self.ACTIVITY_WEIGHTS.get(activity_type, {})

        # 计算时长因子: log(duration + 1)
        duration_factor = math.log(activity.duration_estimate + 1)

        deltas = {}
        for dimension, base_weight in weights.items():
            # delta = base_weight × intensity × log(duration + 1)
            delta_value = base_weight * activity.intensity * duration_factor
            deltas[dimension] = delta_value

        return deltas
```

**Step 2: 提交**

```bash
git add voice-server/app/services/calculator.py
git commit -m "feat: add delta calculator rule engine"
```

---

## Task 9: 数据库模块

**Files:**
- Create: `voice-server/app/db/__init__.py`
- Create: `voice-server/app/db/database.py`

**Step 1: 创建 voice-server/app/db/__init__.py**

```python
from .database import init_db, get_db, DailyRecordDB

__all__ = ["init_db", "get_db", "DailyRecordDB"]
```

**Step 2: 创建 voice-server/app/db/database.py**

```python
import aiosqlite
import uuid
import json
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional
from ..config.settings import get_config
from ..models.schemas import DailyRecord, DailyRecordCreate, Delta


class DailyRecordDB:
    """每日记录数据库操作"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            config = get_config()
            db_path = config.database.path

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """初始化数据库表"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS daily_records (
                    id TEXT PRIMARY KEY,
                    date TEXT NOT NULL UNIQUE,
                    raw_text TEXT NOT NULL,
                    activities_json TEXT NOT NULL,
                    delta_knowledge REAL DEFAULT 0,
                    delta_skill REAL DEFAULT 0,
                    delta_complexity REAL DEFAULT 0,
                    delta_system REAL DEFAULT 0,
                    delta_execution REAL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            await db.commit()

    async def create(self, record: DailyRecordCreate) -> DailyRecord:
        """创建新记录"""
        record_id = str(uuid.uuid4())
        now = datetime.now()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO daily_records (
                    id, date, raw_text, activities_json,
                    delta_knowledge, delta_skill, delta_complexity,
                    delta_system, delta_execution, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record_id,
                record.date.isoformat(),
                record.raw_text,
                json.dumps([act.model_dump() for act in record.activities]),
                record.delta.knowledge_intake,
                record.delta.skill_fluency,
                record.delta.complexity_handling,
                record.delta.system_thinking,
                record.delta.execution,
                now.isoformat()
            ))
            await db.commit()

        return await self.get_by_id(record_id)

    async def get_by_id(self, record_id: str) -> Optional[DailyRecord]:
        """根据 ID 获取记录"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM daily_records WHERE id = ?",
                (record_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return self._row_to_model(row)
        return None

    async def get_by_date(self, date: date) -> Optional[DailyRecord]:
        """根据日期获取记录"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM daily_records WHERE date = ?",
                (date.isoformat(),)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return self._row_to_model(row)
        return None

    async def list_all(self, limit: int = 100) -> List[DailyRecord]:
        """获取所有记录"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM daily_records ORDER BY date DESC LIMIT ?",
                (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_model(row) for row in rows]

    def _row_to_model(self, row) -> DailyRecord:
        """将数据库行转换为模型"""
        activities_data = json.loads(row["activities_json"])

        delta = Delta(
            knowledge_intake=row["delta_knowledge"],
            skill_fluency=row["delta_skill"],
            complexity_handling=row["delta_complexity"],
            system_thinking=row["delta_system"],
            execution=row["delta_execution"]
        )

        return DailyRecord(
            id=row["id"],
            date=date.fromisoformat(row["date"]),
            raw_text=row["raw_text"],
            activities=activities_data,
            delta=delta,
            created_at=datetime.fromisoformat(row["created_at"])
        )


# 全局实例
_db: DailyRecordDB = None


def get_db() -> DailyRecordDB:
    global _db
    if _db is None:
        _db = DailyRecordDB()
    return _db


async def init_db():
    """初始化数据库"""
    db = get_db()
    await db.initialize()
```

**Step 3: 提交**

```bash
git add voice-server/app/db/
git commit -m "feat: add SQLite database module"
```

---

## Task 10: API 路由

**Files:**
- Create: `voice-server/app/api/__init__.py`
- Create: `voice-server/app/api/v1/__init__.py`
- Create: `voice-server/app/api/v1/routes.py`
- Create: `voice-server/app/main.py`

**Step 1: 创建 voice-server/app/api/__init__.py**

```python
from .v1 import router as v1_router

__all__ = ["v1_router"]
```

**Step 2: 创建 voice-server/app/api/v1/__init__.py**

```python
from fastapi import APIRouter
from .routes import router

__all__ = ["router"]
```

**Step 3: 创建 voice-server/app/api/v1/routes.py**

```python
import tempfile
import os
from datetime import date
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional

from ...models.schemas import ProcessResponse, DailyRecord
from ...services.whisper import WhisperClient
from ...services.agent import GrowthAnalysisAgent
from ...services.calculator import DeltaCalculator
from ...db.database import get_db

router = APIRouter(prefix="/api/v1", tags=["v1"])

# 初始化服务
whisper_client = WhisperClient()
agent = GrowthAnalysisAgent()
calculator = DeltaCalculator()


@router.post("/process", response_model=ProcessResponse)
async def process_audio(audio_file: UploadFile = File(...)):
    """
    处理音频文件: 转写 -> 解析 -> 计算
    """

    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        content = await audio_file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    try:
        # Step 1: Whisper 转写
        transcribed_text = await whisper_client.transcribe(tmp_file_path)

        # Step 2: Agent 解析活动
        activities = await agent.analyze(transcribed_text)

        # Step 3: 计算_delta
        delta = calculator.calculate(activities)

        # Step 4: 保存到数据库
        from ...models.schemas import DailyRecordCreate
        record_create = DailyRecordCreate(
            date=date.today(),
            raw_text=transcribed_text,
            activities=activities,
            delta=delta
        )
        db = get_db()
        saved_record = await db.create(record_create)

        return ProcessResponse(
            text=transcribed_text,
            activities=activities,
            delta=delta,
            date=date.today()
        )

    finally:
        # 清理临时文件
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)


@router.get("/records", response_model=list[DailyRecord])
async def get_records(
    date_filter: Optional[date] = Query(None, description="按日期过滤")
):
    """获取历史记录"""
    db = get_db()

    if date_filter:
        record = await db.get_by_date(date_filter)
        return [record] if record else []

    return await db.list_all()


@router.get("/health")
async def health_check():
    """健康检查"""
    db = get_db()
    return {"status": "healthy", "database": str(db.db_path)}
```

**Step 4: 创建 voice-server/app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import get_config
from app.api.v1 import router as v1_router
from app.db.database import init_db


config = get_config()

app = FastAPI(
    title="Growth Engine API",
    description="语音驱动的个人成长量化系统",
    version="0.1.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.server.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(v1_router)


@app.on_event("startup")
async def startup_event():
    """启动时初始化数据库"""
    await init_db()


@app.get("/")
async def root():
    return {
        "message": "Growth Engine API",
        "version": "0.1.0",
        "docs": "/docs"
    }
```

**Step 5: 提交**

```bash
git add voice-server/app/api/ voice-server/app/main.py
git commit -m "feat: add FastAPI routes"
```

---

## Task 11: PySide6 客户端 - API 通信

**Files:**
- Create: `voice-client/services/__init__.py`
- Create: `voice-client/services/api_client.py`

**Step 1: 创建 voice-client/services/__init__.py**

```python
from .api_client import APIClient

__all__ = ["APIClient"]
```

**Step 2: 创建 voice-client/services/api_client.py**

```python
import requests
from pathlib import Path
from typing import Dict, Any


class APIClient:
    """服务器 API 客户端"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"

    def process_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """上传音频文件并获取处理结果"""

        file_path = Path(audio_file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        with open(file_path, "rb") as audio_file:
            files = {"audio_file": (file_path.name, audio_file, "audio/mpeg")}
            response = requests.post(
                f"{self.api_base}/process",
                files=files,
                timeout=300  # 5分钟超时
            )
            response.raise_for_status()
            return response.json()

    def get_records(self, date_filter: str = None) -> list:
        """获取历史记录"""
        params = {"date": date_filter} if date_filter else {}
        response = requests.get(
            f"{self.api_base}/records",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        response = requests.get(f"{self.api_base}/health", timeout=5)
        response.raise_for_status()
        return response.json()
```

**Step 3: 提交**

```bash
git add voice-client/services/
git commit -m "feat: add client API communication module"
```

---

## Task 12: PySide6 客户端 - 主窗口 UI

**Files:**
- Create: `voice-client/ui/__init__.py`
- Create: `voice-client/ui/main_window.py`

**Step 1: 创建 voice-client/ui/__init__.py**

```python
from .main_window import MainWindow

__all__ = ["MainWindow"]
```

**Step 2: 创建 voice-client/ui/main_window.py**

```python
import sys
import tempfile
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QLabel, QMessageBox
)
from PySide6.QtCore import QThread, Signal
import pyaudio
import wave

from ..services.api_client import APIClient


class AudioRecorder(QThread):
    """音频录制线程"""
    finished = signal(str)  # 录制完成,返回文件路径

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
```

**Step 3: 更新 voice-client/main.py**

```python
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

**Step 4: 提交**

```bash
git add voice-client/ui/
git commit -m "feat: add PySide6 main window with recording"
```

---

## Task 13: 创建 README 和运行说明

**Files:**
- Create: `README.md`
- Create: `voice-server/.env.example`
- Create: `voice-client/.env.example`

**Step 1: 创建 README.md**

```markdown
# Growth Engine

语音驱动的个人成长量化系统

## 项目结构

```
myVoice/
├── voice-server/     # 后端服务 (FastAPI)
├── voice-client/     # 客户端 (PySide6)
└── docs/            # 文档
```

## 快速开始

### 1. 安装依赖

**服务器端:**
```bash
cd voice-server
pip install -r requirements.txt
```

**客户端:**
```bash
cd voice-client
pip install -r requirements.txt
```

### 2. 配置 API Keys

复制示例配置并填写你的 API Keys:

```bash
cd voice-server
cp config.yaml.example config.yaml
# 编辑 config.yaml,填写 deepseek 和 whisper API keys
```

### 3. 启动服务器

```bash
cd voice-server
python run.py
```

服务器将在 http://127.0.0.1:8000 启动

API 文档: http://127.0.0.1:8000/docs

### 4. 启动客户端

```bash
cd voice-client
python main.py
```

## 功能特性

- 🎤 语音录音转文本 (Whisper API)
- 🤖 AI 活动解析 (DeepSeek 多步骤推理)
- 📊 成长增量计算 (规则引擎)
- 💾 数据持久化 (SQLite)

## 技术栈

- **后端**: FastAPI, SQLite, httpx, Jinja2
- **前端**: PySide6, PyAudio
- **AI**: OpenAI Whisper, DeepSeek Chat

## License

MIT
```

**Step 2: 创建 voice-server/.env.example**

```env
# DeepSeek API Key
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Whisper API Key
WHISPER_API_KEY=your_whisper_api_key_here
```

**Step 3: 创建 voice-client/.env.example**

```env
# Server URL
SERVER_URL=http://127.0.0.1:8000
```

**Step 4: 提交**

```bash
git add README.md voice-server/.env.example voice-client/.env.example
git commit -m "docs: add README and setup instructions"
```

---

## Task 14: 测试与验证

**Files:**
- Create: `voice-server/tests/__init__.py`
- Create: `voice-server/tests/test_calculator.py`
- Create: `voice-server/tests/test_agent.py`

**Step 1: 创建测试目录和文件**

```bash
mkdir -p voice-server/tests
touch voice-server/tests/__init__.py
```

**Step 2: 创建 voice-server/tests/test_calculator.py**

```python
import pytest
from app.services.calculator import DeltaCalculator
from app.models.schemas import Activity, ActivityType


def test_calculate_single_activity():
    """测试单个活动的 delta 计算"""
    calculator = DeltaCalculator()

    activity = Activity(
        type=ActivityType.ACTIVE_PRACTICE,
        topic="LeetCode",
        description="刷算法题",
        intensity=0.8,
        duration_estimate=2.0
    )

    result = calculator.calculate([activity])

    assert result.skill_fluency > 0
    assert result.execution > 0
    assert result.skill_fluency <= 0.3  # 上限检查


def test_calculate_multiple_activities():
    """测试多个活动的累计 delta"""
    calculator = DeltaCalculator()

    activities = [
        Activity(
            type=ActivityType.LEARNING_INPUT,
            topic="Python教程",
            description="看视频学习",
            intensity=0.6,
            duration_estimate=2.0
        ),
        Activity(
            type=ActivityType.ACTIVE_PRACTICE,
            topic="LeetCode",
            description="刷题",
            intensity=0.8,
            duration_estimate=1.5
        )
    ]

    result = calculator.calculate(activities)

    assert result.knowledge_intake > 0
    assert result.skill_fluency > 0
    assert result.execution > 0


def test_max_delta_limit():
    """测试单维度上限"""
    calculator = DeltaCalculator()

    # 创建大量高强度活动
    activities = [
        Activity(
            type=ActivityType.ACTIVE_PRACTICE,
            topic=f"Activity {i}",
            description="Test",
            intensity=1.0,
            duration_estimate=10.0
        )
        for i in range(100)
    ]

    result = calculator.calculate(activities)

    # 所有维度都不应超过上限
    assert result.skill_fluency <= 0.3
    assert result.execution <= 0.3
```

**Step 3: 创建 voice-server/tests/test_agent.py**

```python
import pytest
from app.services.agent import GrowthAnalysisAgent
from app.services.deepseek import DeepSeekClient


@pytest.mark.asyncio
async def test_agent_analyze():
    """测试 Agent 分析流程"""
    # 注意: 需要有效的 API key 才能运行此测试
    agent = GrowthAnalysisAgent()

    text = "今天刷了两小时LeetCode,调试了一个并发问题。"

    activities = await agent.analyze(text)

    assert len(activities) > 0
    assert all(hasattr(act, 'type') for act in activities)
    assert all(hasattr(act, 'intensity') for act in activities)
    assert all(0 <= act.intensity <= 1 for act in activities)


@pytest.mark.asyncio
async def test_step1_extract():
    """测试活动提取步骤"""
    agent = GrowthAnalysisAgent()

    text = "今天看了三小时Python教程,然后刷了LeetCode。"

    activities = await agent._step1_extract(text)

    assert isinstance(activities, list)
    assert len(activities) > 0
```

**Step 4: 提交**

```bash
git add voice-server/tests/
git commit -m "test: add unit tests for calculator and agent"
```

---

## 验收检查清单

完成所有任务后,验证以下功能:

- [ ] 服务器成功启动 (`python voice-server/run.py`)
- [ ] 访问 API 文档 (http://127.0.0.1:8000/docs)
- [ ] 健康检查通过 (GET /api/v1/health)
- [ ] 客户端成功启动 (`python voice-client/main.py`)
- [ ] 客户端可以录音
- [ ] 上传音频后成功转写
- [ ] Agent 正确解析活动
- [ ] Delta 计算正确
- [ ] 数据成功保存到 SQLite
- [ ] 可以查询历史记录

---

## 执行计划

本实现计划已保存到 `docs/plans/2026-02-20-growth-engine-implementation.md`

**两种执行方式:**

**1. Subagent-Driven (当前会话)** - 我为每个任务调度新的子代理,任务之间进行代码审查,快速迭代

**2. Parallel Session (独立会话)** - 在新会话中使用 executing-plans skill,批量执行并有检查点

你想选择哪种方式?
