from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

from .agents import PlannerAgent, CoderAgent, ReviewerAgent, TesterAgent
from .client import LLMClient
from .config import Config
from .rag import Retriever
from .tools.registry import ToolRegistry

console = Console()

MAX_FIX_ROUNDS = 3


@dataclass
class FlowResult:
    plan: str = ""
    code: str = ""
    review: str = ""
    tests: str = ""
    fix_history: list[str] = None

    def __post_init__(self):
        if self.fix_history is None:
            self.fix_history = []

    @property
    def report(self) -> str:
        sections = []
        if self.plan:
            sections.append(f"## Development Plan\n{self.plan}")
        if self.code:
            sections.append(f"## Generated Code\n{self.code}")
        if self.review:
            sections.append(f"## Code Review\n{self.review}")
        for i, fix in enumerate(self.fix_history, 1):
            sections.append(f"## Fix Round {i}\n{fix}")
        if self.tests:
            sections.append(f"## Test Cases\n{self.tests}")
        return "\n\n---\n\n".join(sections)


class DevFlow:
    def __init__(
        self,
        config: Config | None = None,
        tools: ToolRegistry | None = None,
        retriever: Retriever | None = None,
    ):
        self.config = config or Config()
        self.client = LLMClient(self.config)
        self.tools = tools or ToolRegistry()
        self.retriever = retriever or Retriever()
        self._shared_client = False

        self.planner = PlannerAgent(self.client, config=self.config, tools=self.tools)
        self.coder = CoderAgent(self.client, config=self.config, tools=self.tools)
        self.reviewer = ReviewerAgent(self.client, config=self.config, tools=self.tools)
        self.tester = TesterAgent(self.client, config=self.config, tools=self.tools)
        self._agents = [self.planner, self.coder, self.reviewer, self.tester]

    async def run(self, requirement: str, *, mode: str = "full") -> FlowResult:
        result = FlowResult()

        # Retrieve RAG context if documents are loaded
        rag_context = ""
        if self.retriever.chunk_count > 0:
            hits = await self.retriever.query(requirement, top_k=5)
            if hits:
                rag_context = self.retriever.build_context(hits)

        with Progress() as progress:
            if mode in ("full", "plan"):
                task = progress.add_task("[cyan]Planning...", total=1)
                result.plan = await self.planner.run(requirement, context=rag_context)
                progress.update(task, completed=1)
                console.print(Panel(result.plan[:500], title="Plan", border_style="cyan"))

            if mode in ("full", "code"):
                task = progress.add_task("[green]Coding...", total=1)
                code_input = f"需求：{requirement}\n\n计划：{result.plan}" if result.plan else requirement
                result.code = await self.coder.run(code_input, context=rag_context)
                progress.update(task, completed=1)
                console.print(Panel(result.code[:500], title="Code", border_style="green"))

            if mode in ("full", "review"):
                task = progress.add_task("[yellow]Reviewing...", total=1)
                review_input = f"需求：{requirement}\n\n代码：{result.code}" if result.code else requirement
                result.review = await self.reviewer.run(review_input, context=rag_context)
                progress.update(task, completed=1)
                console.print(Panel(result.review[:500], title="Review", border_style="yellow"))

                # Iterative fix loop if review found issues
                if mode == "full" and "不通过" in result.review or "需修改" in result.review:
                    for round_num in range(MAX_FIX_ROUNDS):
                        fix_task = progress.add_task(f"[red]Fixing (round {round_num + 1})...", total=1)
                        fix_input = (
                            f"需求：{requirement}\n\n当前代码：{result.code}\n\n"
                            f"审查意见：{result.review}\n\n请修复上述问题，输出完整修正后的代码。"
                        )
                        fixed_code = await self.coder.run(fix_input, context=rag_context)
                        re_review_input = f"需求：{requirement}\n\n代码：{fixed_code}"
                        re_review = await self.reviewer.run(re_review_input, context=rag_context)
                        result.code = fixed_code
                        result.fix_history.append(re_review)
                        progress.update(fix_task, completed=1)
                        if "不通过" not in re_review and "需修改" not in re_review:
                            result.review = re_review
                            break

            if mode in ("full", "test"):
                task = progress.add_task("[magenta]Testing...", total=1)
                test_input = f"需求：{requirement}\n\n代码：{result.code}" if result.code else requirement
                result.tests = await self.tester.run(test_input, context=rag_context)
                progress.update(task, completed=1)
                console.print(Panel(result.tests[:500], title="Tests", border_style="magenta"))

        return result

    async def close(self):
        for agent in self._agents:
            await agent.close()
