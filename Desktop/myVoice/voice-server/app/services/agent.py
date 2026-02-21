import asyncio
import json
from typing import List, Dict
from .deepseek import DeepSeekClient
from ..prompts.manager import get_prompt_manager
from ..models.schemas import Activity


class GrowthAnalysisAgent:
    """成长分析 Agent - 多步骤推理"""

    def __init__(self, deepseek_client: DeepSeekClient = None, progress_callback: callable = None):
        self.deepseek = deepseek_client or DeepSeekClient()
        self.prompts = get_prompt_manager()
        self.progress_callback = progress_callback

    def _log_progress(self, step: str, message: str):
        """输出推理进度"""
        if self.progress_callback:
            self.progress_callback(step, message)
        print(f"[{step}] {message}")  # 终端输出

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
        self._log_progress("STEP 1", "提取活动中...")
        prompt = self.prompts.get_extract_prompt(text)
        response = await self.deepseek.chat_with_json(
            user_prompt=prompt,
            system_prompt=self.prompts.get_system_prompt()
        )
        result = response.get("activities", [])
        self._log_progress("STEP 1", f"✓ 提取完成 ({len(result)}个活动)")
        return result

    async def _step2_classify(self, activities: List[Dict]) -> List[Dict]:
        """并行分类所有活动"""
        self._log_progress("STEP 2", f"分类活动 ({len(activities)}个)...")
        tasks = [
            self._classify_single_activity(activity)
            for activity in activities
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 过滤异常结果
        valid_results = [r for r in results if not isinstance(r, Exception)]
        self._log_progress("STEP 2", "✓ 分类完成")
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
        self._log_progress("STEP 3", "评估活动强度...")
        tasks = [
            self._evaluate_single_activity(activity)
            for activity in classified_activities
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 过滤异常结果
        valid_results = [r for r in results if not isinstance(r, Exception)]
        self._log_progress("STEP 3", "✓ 评估完成")
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