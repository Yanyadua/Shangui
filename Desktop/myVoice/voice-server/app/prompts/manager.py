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