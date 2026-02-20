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