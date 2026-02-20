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