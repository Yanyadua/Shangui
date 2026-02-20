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