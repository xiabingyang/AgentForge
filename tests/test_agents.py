import pytest

from agentforge.config import Config
from agentforge.agents import PlannerAgent, CoderAgent, ReviewerAgent, TesterAgent


@pytest.mark.parametrize("agent_cls", [PlannerAgent, CoderAgent, ReviewerAgent, TesterAgent])
def test_agent_has_name(agent_cls):
    agent = agent_cls(config=Config(api_key="test"))
    assert agent.name
    assert agent.system_prompt


def test_planner_system_prompt():
    agent = PlannerAgent(config=Config(api_key="test"))
    assert "任务" in agent.system_prompt


def test_coder_system_prompt():
    agent = CoderAgent(config=Config(api_key="test"))
    assert "代码" in agent.system_prompt


def test_reviewer_system_prompt():
    agent = ReviewerAgent(config=Config(api_key="test"))
    assert "审查" in agent.system_prompt


def test_tester_system_prompt():
    agent = TesterAgent(config=Config(api_key="test"))
    assert "测试" in agent.system_prompt
