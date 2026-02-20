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