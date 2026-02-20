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