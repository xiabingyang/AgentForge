"""项目规划示例"""

import asyncio

from flowpilot import DevFlow


async def main():
    flow = DevFlow()

    requirement = """
    构建一个在线协作文档编辑器，核心功能：
    - 实时多人协作编辑（类似 Google Docs）
    - 支持 Markdown 和富文本模式
    - 文档版本历史和回滚
    - 评论和批注功能
    - 权限管理（查看/编辑/管理）
    """

    try:
        result = await flow.run(requirement, mode="plan")
        print(result.plan)
    finally:
        await flow.close()


if __name__ == "__main__":
    asyncio.run(main())
