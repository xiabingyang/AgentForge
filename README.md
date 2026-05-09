# AgentForge

基于多 Agent 协作的智能开发工作流框架，支持任意 OpenAI 兼容 API（OpenAI、MiMo、DeepSeek 等）。

## 特性

- **多 Agent 协作** — Planner、Coder、Reviewer、Tester 四大 Agent 分工协作
- **工具调用 (Function Calling)** — Agent 可调用文件读写、代码分析、Shell 命令等工具，自主完成任务
- **RAG 知识库** — 上传文档构建知识库，Agent 基于检索内容回答问题
- **迭代修复循环** — Reviewer 审查不通过时自动触发 Coder 修复，最多 3 轮
- **Web 界面** — Streamlit 驱动的交互式 UI，支持对话式操作和文件上传
- **长链推理** — 需求分析 → 任务拆解 → 代码生成 → 交叉审查 → 自动修复 → 测试验证
- **多后端支持** — 任何 OpenAI 兼容 API 即插即用，切换只需改环境变量
- **可扩展** — 轻松添加自定义 Agent、工具和 Chunk 策略

## 架构

```
┌─────────────────────────────────────────────────────┐
│                    Web UI (Streamlit)                │
│               CLI / Programmatic API                 │
├─────────────────────────────────────────────────────┤
│                   Orchestrator                       │
│          (编排调度 + 迭代修复循环)                    │
├────────┬────────┬──────────┬────────────────────────┤
│Planner│ Coder  │ Reviewer │       Tester            │
│(规划) │(编码)  │  (审查)  │      (测试)             │
│        │        │          │                         │
│    Tool Calling  │  RAG Context                     │
│  ┌──────────┐   │  ┌──────────────┐                │
│  │Tool Reg. │   │  │  VectorStore │                │
│  │File Ops  │   │  │  Embeddings  │                │
│  │Analysis  │   │  │  Chunker     │                │
│  │Shell     │   │  └──────────────┘                │
│  └──────────┘   │                                   │
├─────────────────┴───────────────────────────────────┤
│               LLM Client (OpenAI Compatible)         │
└─────────────────────────────────────────────────────┘
```

## 工作流程

1. **Planner** — 分析需求，将复杂任务分解为有序子任务
2. **Coder** — 根据计划生成代码，可调用工具读写文件、分析代码
3. **Reviewer** — 从正确性、安全性、性能、可维护性多维度审查
4. **迭代修复** — 审查不通过时自动触发 Coder 修复，最多 3 轮
5. **Tester** — 根据最终代码生成测试用例
6. **Orchestrator** — 协调全流程，注入 RAG 上下文

## 快速开始

```bash
pip install -e .
```

```bash
cp .env.example .env
# 编辑 .env 配置 API Key 和 Base URL
```

### 启动 Web 界面

```bash
streamlit run agentforge/web/app.py
```

Web 界面支持：
- 交互式对话，选择不同运行模式
- 上传文档到知识库（RAG）
- 实时查看 Plan / Code / Review / Test 结果
- 切换 LLM 后端

### 命令行使用

```bash
# 完整开发流程（规划 → 编码 → 审查 → 修复 → 测试）
python -m agentforge "实现一个带邮箱验证的用户注册 API"

# 仅代码审查
python -m agentforge --mode review --file path/to/code.py

# 仅生成开发计划
python -m agentforge --mode plan "构建一个博客系统"
```

### 代码调用

```python
import asyncio
from agentforge import DevFlow

async def main():
    flow = DevFlow()
    result = await flow.run("实现一个 RESTful 用户管理 API")
    print(result.report)

asyncio.run(main())
```

### 使用 RAG 知识库

```python
import asyncio
from agentforge import DevFlow, Retriever

async def main():
    retriever = Retriever()
    # 上传文档到知识库
    await retriever.add_text("项目架构文档内容...", source="architecture.md")

    flow = DevFlow(retriever=retriever)
    result = await flow.run("根据架构文档实现用户模块")
    print(result.report)

asyncio.run(main())
```

### 自定义工具

```python
from agentforge.tools import ToolDefinition, ToolParameter, registry

registry.register(ToolDefinition(
    name="my_tool",
    description="自定义工具描述",
    parameters=[ToolParameter("input", "string", "输入参数")],
    handler=lambda input: f"处理结果: {input}",
))
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
agentforge/
├── __init__.py          # 公开 API
├── __main__.py          # CLI 入口
├── config.py            # 配置管理
├── client.py            # LLM API 客户端（支持流式）
├── orchestrator.py      # 多 Agent 编排器 + 迭代修复
├── agents/
│   ├── base.py          # Agent 基类（含工具调用）
│   ├── planner.py       # 规划 Agent
│   ├── coder.py         # 编码 Agent
│   ├── reviewer.py      # 审查 Agent
│   └── tester.py        # 测试 Agent
├── tools/
│   ├── registry.py      # 工具注册中心
│   ├── file_ops.py      # 文件读写
│   ├── code_analysis.py # 代码分析（AST）
│   └── shell.py         # Shell 执行（安全白名单）
├── rag/
│   ├── document.py      # 文档加载
│   ├── chunker.py       # 文本分块
│   ├── embedder.py      # 文本向量化
│   ├── vectorstore.py   # 向量存储
│   └── retriever.py     # 检索器
├── web/
│   └── app.py           # Streamlit Web 界面
└── prompts/
    └── templates.py
examples/                # 使用示例
tests/                   # 26 个测试用例
```

## Tech Stack

- **Python 3.10+**
- **httpx** — 异步 HTTP 客户端
- **numpy** — 向量计算
- **streamlit** — Web 界面
- **rich** — CLI 终端美化
- **pydantic** — 数据校验

## License

MIT
