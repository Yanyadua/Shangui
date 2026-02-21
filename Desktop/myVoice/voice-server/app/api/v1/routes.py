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

    def progress_callback(step: str, message: str):
        """推理进度回调 - 输出到终端"""
        print(f"[{step}] {message}")

    # 创建带进度回调的agent
    agent_with_progress = GrowthAnalysisAgent(progress_callback=progress_callback)

    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        content = await audio_file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    try:
        # Step 1: Whisper 转写
        transcribed_text = await whisper_client.transcribe(tmp_file_path)

        # Step 2: Agent 解析活动（使用带进度回调的agent）
        activities = await agent_with_progress.analyze(transcribed_text)

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