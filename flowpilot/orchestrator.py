from __future__ import annotations

import json
from dataclasses import dataclass, field

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

from .agents import PlannerAgent, CoderAgent, ReviewerAgent, TesterAgent
from .client import LLMClient
from .config import Config

console = Console()


@dataclass
class FlowResult:
    plan: str = ""
    code: str = ""
    review: str = ""
    tests: str = ""

    @property
    def report(self) -> str:
        sections = []
        if self.plan:
            sections.append(f"## 开发计划\n{self.plan}")
        if self.code:
            sections.append(f"## 生成的代码\n{self.code}")
        if self.review:
            sections.append(f"## 审查报告\n{self.review}")
        if self.tests:
            sections.append(f"## 测试用例\n{self.tests}")
        return "\n\n---\n\n".join(sections)


class DevFlow:
    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.client = LLMClient(self.config)
        self.planner = PlannerAgent(self.client)
        self.coder = CoderAgent(self.client)
        self.reviewer = ReviewerAgent(self.client)
        self.tester = TesterAgent(self.client)
        self._agents = [self.planner, self.coder, self.reviewer, self.tester]

    async def run(self, requirement: str, *, mode: str = "full") -> FlowResult:
        result = FlowResult()

        with Progress() as progress:
            if mode in ("full", "plan"):
                task = progress.add_task("[cyan]Planning...", total=1)
                result.plan = await self.planner.run(requirement)
                progress.update(task, completed=1)
                console.print(Panel(result.plan[:500], title="Plan", border_style="cyan"))

            if mode in ("full", "code"):
                task = progress.add_task("[green]Coding...", total=1)
                code_context = f"需求：{requirement}\n\n开发计划：{result.plan}" if result.plan else requirement
                result.code = await self.coder.run(code_context)
                progress.update(task, completed=1)
                console.print(Panel(result.code[:500], title="Code", border_style="green"))

            if mode in ("full", "review"):
                task = progress.add_task("[yellow]Reviewing...", total=1)
                review_input = f"需求：{requirement}\n\n代码：{result.code}" if result.code else requirement
                result.review = await self.reviewer.run(review_input)
                progress.update(task, completed=1)
                console.print(Panel(result.review[:500], title="Review", border_style="yellow"))

            if mode in ("full", "test"):
                task = progress.add_task("[magenta]Testing...", total=1)
                test_input = f"需求：{requirement}\n\n代码：{result.code}" if result.code else requirement
                result.tests = await self.tester.run(test_input)
                progress.update(task, completed=1)
                console.print(Panel(result.tests[:500], title="Tests", border_style="magenta"))

        return result

    async def close(self):
        for agent in self._agents:
            await agent.close()
