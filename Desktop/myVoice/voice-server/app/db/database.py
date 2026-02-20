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