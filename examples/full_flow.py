"""完整开发流程示例：规划 → 编码 → 审查 → 测试"""

import asyncio

from agentforge import DevFlow


async def main():
    flow = DevFlow()

    requirement = """
    实现一个 Python 任务队列系统，要求：
    1. 支持异步任务提交和执行
    2. 支持任务优先级
    3. 支持任务重试（最多3次）
    4. 支持并发控制（最大 worker 数）
    5. 提供任务状态查询接口
    """

    try:
        result = await flow.run(requirement)
        print(result.report)
    finally:
        await flow.close()


if __name__ == "__main__":
    asyncio.run(main())
