from typing import Any

from inline_snapshot import snapshot

from meta_loop import eval


class MockPart:
    def __init__(self, tool_name: str, part_kind: str, tool_call_id: str):
        self.tool_name = tool_name
        self.part_kind = part_kind
        self.tool_call_id = tool_call_id


class MockMessage:
    def __init__(self, parts: list[Any]):
        self.parts = parts


def make_result(messages):
    return type("MockRunResult", (), {"_all_messages": messages})()


def test_basic():
    given = [
        MockMessage([]),
        MockMessage([MockPart("create_agent_workdir", "tool-call", "call_0_1")]),
        MockMessage([]),
        MockMessage([MockPart("write_code", "tool-call", "call_0_2")]),
        MockMessage([]),
        MockMessage([MockPart("write_test_code", "tool-call", "call_0_3")]),
        MockMessage([]),
        MockMessage([MockPart("run_pytest_test_code", "tool-call", "call_0_4")]),
        MockMessage([]),
        MockMessage([MockPart("run_pre_commit", "tool-call", "call_0_5")]),
        MockMessage([]),
        MockMessage(
            [
                MockPart("evaluate_code", "tool-call", "call_0_6"),
                MockPart("run_pytest_test_code", "tool-call", "call_1_7"),
            ]
        ),
        MockMessage([]),
    ]
    score, cycles, coverage, tool_usage = eval.evaluate_run_result(
        make_result(given), max_tools=7
    )
    assert score == snapshot(9.32)


def test_empty():
    given = []
    score, cycles, coverage, tool_usage = eval.evaluate_run_result(
        make_result(given), max_tools=7
    )
    assert score == snapshot(0.0)


def test_repeated():
    given = [
        MockMessage([]),
        MockMessage([MockPart("create_agent_workdir", "tool-call", "call_0_1")]),
        MockMessage([]),
        MockMessage([MockPart("write_code", "tool-call", "call_0_2")]),
        MockMessage([]),
        MockMessage([MockPart("write_test_code", "tool-call", "call_0_3")]),
        MockMessage([MockPart("write_test_code", "tool-call", "call_0_3")]),
        MockMessage([MockPart("write_test_code", "tool-call", "call_0_3")]),
        MockMessage([MockPart("write_test_code", "tool-call", "call_0_3")]),
        MockMessage([MockPart("write_test_code", "tool-call", "call_0_3")]),
        MockMessage([MockPart("write_test_code", "tool-call", "call_0_3")]),
        MockMessage([MockPart("write_test_code", "tool-call", "call_0_3")]),
        MockMessage([MockPart("write_test_code", "tool-call", "call_0_3")]),
        MockMessage([MockPart("write_test_code", "tool-call", "call_0_3")]),
    ]

    score, cycles, coverage, tool_usage = eval.evaluate_run_result(
        make_result(given), max_tools=7
    )
    assert score == snapshot(5.32)
