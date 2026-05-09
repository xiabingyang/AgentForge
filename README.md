# FlowPilot

基于多 Agent 协作的智能开发工作流框架，支持任意 OpenAI 兼容 API（OpenAI、MiMo、DeepSeek 等）。

## 特性

- **多 Agent 协作** — Planner、Coder、Reviewer、Tester 四大 Agent 分工协作
- **长链推理** — 需求分析 → 任务拆解 → 代码生成 → 交叉审查 → 测试验证
- **多后端支持** — 任何 OpenAI 兼容 API 即插即用
- **流式输出** — 支持流式响应，实时查看生成过程
- **可扩展** — 轻松添加自定义 Agent 和工具

## 架构

```
                    ┌──────────────────┐
                    │   Orchestrator   │
                    │  (任务编排调度)   │
                    └──┬───┬───┬───┬──┘
                       │   │   │   │
                 ┌─────┘   │   │   └─────┐
                 ▼         ▼   ▼         ▼
             Planner   Coder  Reviewer  Tester
             (规划)    (编码)  (审查)    (测试)
                 │         │   │         │
                 └────┬────┘   └────┬────┘
                      ▼             ▼
              ┌──────────────────────────┐
              │     LLM Client Layer     │
              │  (OpenAI Compatible API)  │
              └──────────────────────────┘
```

## 工作流程

1. **Planner** — 分析需求，将复杂任务分解为有序子任务
2. **Coder** — 根据计划逐个实现子任务，生成代码
3. **Reviewer** — 从正确性、安全性、性能、可维护性多维度审查
4. **Tester** — 根据代码和需求生成测试用例
5. **Orchestrator** — 协调全流程，汇总各 Agent 输出

## 快速开始

```bash
pip install -e .
```

```bash
cp .env.example .env
# 编辑 .env 配置 API Key 和 Base URL
```

### 命令行使用

```bash
# 完整开发流程（规划 → 编码 → 审查 → 测试）
python -m flowpilot "实现一个带邮箱验证的用户注册 API"

# 仅代码审查
python -m flowpilot --mode review --file path/to/code.py

# 仅生成开发计划
python -m flowpilot --mode plan "构建一个博客系统"
```

### 代码调用

```python
import asyncio
from flowpilot import DevFlow

async def main():
    flow = DevFlow()
    result = await flow.run("实现一个 RESTful 用户管理 API")
    print(result.report)

asyncio.run(main())
```

## 配置

通过环境变量或 `.env` 文件配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_API_KEY` | API 密钥 | — |
| `LLM_BASE_URL` | API 基础地址 | `https://api.openai.com/v1` |
| `LLM_MODEL` | 模型名称 | `gpt-4o` |
| `LLM_TEMPERATURE` | 温度参数 | `0.7` |
| `LLM_MAX_TOKENS` | 最大 Token 数 | `4096` |

切换后端只需修改 `LLM_BASE_URL` 和 `LLM_MODEL`，例如：

```bash
# 使用 MiMo
LLM_BASE_URL=https://api.xiaomimimo.com/v1 LLM_MODEL=mimo-v2.5-pro

# 使用 DeepSeek
LLM_BASE_URL=https://api.deepseek.com/v1 LLM_MODEL=deepseek-chat
```

## 项目结构

```
flowpilot/
├── __init__.py          # 公开 API
├── __main__.py          # CLI 入口
├── config.py            # 配置管理
├── client.py            # LLM API 客户端
├── orchestrator.py      # 多 Agent 编排器
├── agents/
│   ├── base.py          # Agent 基类
│   ├── planner.py       # 规划 Agent
│   ├── coder.py         # 编码 Agent
│   ├── reviewer.py      # 审查 Agent
│   └── tester.py        # 测试 Agent
└── prompts/
    └── templates.py     # Prompt 模板
examples/                # 使用示例
tests/                   # 测试
```

## License

MIT
