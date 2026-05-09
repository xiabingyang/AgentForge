import argparse
import asyncio

from rich.console import Console

from .config import Config
from .orchestrator import DevFlow

console = Console()


def main():
    parser = argparse.ArgumentParser(
        prog="flowpilot",
        description="Multi-agent development workflow powered by LLM",
    )
    parser.add_argument("requirement", help="需求描述")
    parser.add_argument(
        "--mode",
        choices=["full", "plan", "code", "review", "test"],
        default="full",
        help="运行模式 (默认: full)",
    )
    parser.add_argument("--model", default=None, help="模型名称")
    parser.add_argument("--base-url", default=None, help="API Base URL")
    parser.add_argument("--api-key", default=None, help="API Key")

    args = parser.parse_args()

    config = Config()
    if args.api_key:
        config.api_key = args.api_key
    if args.base_url:
        config.base_url = args.base_url
    if args.model:
        config.model = args.model

    if not config.api_key:
        console.print("[red]Error: LLM_API_KEY not set. Use .env file or --api-key flag.[/red]")
        raise SystemExit(1)

    flow = DevFlow(config)

    try:
        result = asyncio.run(flow.run(args.requirement, mode=args.mode))
        console.print("\n")
        console.rule("[bold blue]FlowPilot Result")
        console.print(result.report)
    finally:
        asyncio.run(flow.close())


if __name__ == "__main__":
    main()
