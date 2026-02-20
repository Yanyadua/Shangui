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