from datetime import datetime
from typing import Any


def heuristic_function(
    number_of_cycles: int,
    coverage: int,
    max_tools: int,
    tool_usage: dict[str, int],
    success_rate: float,
    duration: float = None,
    max_duration: float = 120.0,  # Default 2 minutes
    output_quality: float = 1.0,  # Default assumes success
) -> float:
    """
    Enhanced heuristic to evaluate AI agent performance with multiple metrics.

    Args:
        number_of_cycles (int): Total number of tool calls (1 to 10).
        coverage (int): Number of unique tools used (1 to max_tools).
        max_tools (int): Total number of available tools.
        tool_usage (Dict[str, int]): Count of each tool's usage.
        success_rate (float): Proportion of successful tool calls (0 to 1).
        duration (float, optional): Total execution time in seconds.
        max_duration (float): Maximum expected duration in seconds (default 120).
        output_quality (float): Quality of final output (0 to 1, default 1).

    Returns:
        float: Score from 0 to 10, rounded to 2 decimal places.
    """
    if not 1 <= number_of_cycles <= 10:
        raise ValueError("Number of cycles must be between 1 and 10.")
    if not 1 <= coverage <= max_tools:
        raise ValueError(f"Coverage must be between 1 and {max_tools}.")
    if coverage > number_of_cycles:
        raise ValueError("Coverage cannot exceed the number of cycles.")
    if max_tools < 1:
        raise ValueError("max_tools must be at least 1.")
    if not 0 <= success_rate <= 1:
        raise ValueError("Success rate must be between 0 and 1.")
    if duration is not None and duration < 0:
        raise ValueError("Duration cannot be negative.")

    # 1. Cycle Score (0 to 2.5): Efficiency in tool calls
    if 5 <= number_of_cycles <= 7:
        cycle_score = 2.5
    elif number_of_cycles < 5:
        cycle_score = (number_of_cycles - 1) * (2.5 / 4)
    else:
        cycle_score = 2.5 - (number_of_cycles - 7) * (2.5 / 3)

    # 2. Coverage Score (0 to 2.5): Proportion of tools used
    coverage_score = (coverage / max_tools) * 2.5

    # 3. Repetition Penalty (0 to -1): Penalize if any tool dominates
    max_repeats = max(tool_usage.values()) if tool_usage else 0
    repetition_penalty = min(1.0, (max_repeats / number_of_cycles) * 2)  # Up to -1

    # 4. Success Score (0 to 2.5): Reward successful tool calls
    success_score = success_rate * 2.5

    # 5. Time Efficiency Score (0 to 2.5): Reward faster execution
    if duration is None:
        time_score = 2.5  # Assume optimal if no duration provided
    else:
        time_score = max(0, 2.5 * (1 - duration / max_duration))  # Linear drop-off

    # 6. Output Quality Bonus (0 to 0.5): Small bonus for good output
    quality_bonus = output_quality * 0.5

    # Total score: Sum components, capped at 10
    total_score = (
        cycle_score
        + coverage_score
        - repetition_penalty
        + success_score
        + time_score
        + quality_bonus
    )
    return round(max(0, min(10, total_score)), 2)


def evaluate_run_result(
    run_result: Any, max_tools: int = 7
) -> tuple[float, int, int, dict[str, int]]:
    """
    Evaluate a RunResult-like object with enhanced metrics.

    Args:
        run_result (Any): Object with '_all_messages' attribute.
        max_tools (int): Total number of available tools (default 7).

    Returns:
        tuple: (score, number_of_cycles, coverage, tool_usage)
    """
    if not hasattr(run_result, "_all_messages"):
        raise ValueError("RunResult object must have '_all_messages' attribute.")

    # Extract tool calls and returns
    tool_calls = []
    tool_returns = []
    timestamps = []
    for message in run_result._all_messages:
        if hasattr(message, "parts"):
            for part in message.parts:
                if hasattr(part, "part_kind"):
                    if part.part_kind == "tool-call" and hasattr(part, "tool_name"):
                        tool_calls.append(part)
                    elif part.part_kind == "tool-return" and hasattr(part, "content"):
                        tool_returns.append(part)
                if hasattr(part, "timestamp"):
                    timestamps.append(part.timestamp)

    number_of_cycles = len(tool_calls)
    if number_of_cycles == 0:
        return 0.0, 0, 0, {}

    # Tool usage and coverage
    tool_usage: dict[str, int] = {}
    for tool_call in tool_calls:
        tool_name = tool_call.tool_name
        tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
    coverage = len(tool_usage)

    # Success rate: Check tool returns for errors
    success_count = sum(
        1
        for ret in tool_returns
        if ret.content and "error" not in str(ret.content).lower()
    )
    success_rate = success_count / len(tool_returns) if tool_returns else 1.0

    # Duration: From first to last timestamp (if available)
    duration = None
    if timestamps and len(timestamps) > 1:
        duration = (timestamps[-1] - timestamps[0]).total_seconds()

    # Output quality: Check if final data indicates success
    output_quality = (
        1.0
        if hasattr(run_result, "data")
        and "successfully" in str(run_result.data).lower()
        else 0.5
    )

    # Cap cycles at 10
    number_of_cycles = min(number_of_cycles, 10)

    # Compute score
    score = heuristic_function(
        number_of_cycles,
        coverage,
        max_tools,
        tool_usage,
        success_rate,
        duration,
        max_duration=120.0,
        output_quality=output_quality,
    )

    return score, number_of_cycles, coverage, tool_usage


def evaluate_map(results: list[Any], max_tools: int = 7):
    score, *_ = evaluate_run_result(results, max_tools)
    return (results, score)


# Example usage
if __name__ == "__main__":

    class MockPart:
        def __init__(
            self,
            tool_name: str,
            part_kind: str,
            tool_call_id: str,
            content: Any = None,
            timestamp: datetime = None,
        ):
            self.tool_name = tool_name
            self.part_kind = part_kind
            self.tool_call_id = tool_call_id
            self.content = content
            self.timestamp = timestamp or datetime(2025, 2, 23, 20, 16, 45)

    class MockMessage:
        def __init__(self, parts: list[Any]):
            self.parts = parts

    mock_run_result = type(
        "MockRunResult",
        (),
        {
            "_all_messages": [
                MockMessage(
                    [
                        MockPart(
                            "create_agent_workdir",
                            "tool-call",
                            "call_0_1",
                            timestamp=datetime(2025, 2, 23, 20, 16, 45),
                        )
                    ]
                ),
                MockMessage(
                    [
                        MockPart(
                            "", "tool-return", "call_0_1", "sandbox/v1/calculator_agent"
                        )
                    ]
                ),
                MockMessage([MockPart("write_code", "tool-call", "call_0_2")]),
                MockMessage([MockPart("", "tool-return", "call_0_2", None)]),
                MockMessage([MockPart("write_test_code", "tool-call", "call_0_3")]),
                MockMessage([MockPart("", "tool-return", "call_0_3", None)]),
                MockMessage(
                    [MockPart("run_pytest_test_code", "tool-call", "call_0_4")]
                ),
                MockMessage([MockPart("", "tool-return", "call_0_4", "4 passed")]),
                MockMessage([MockPart("run_pre_commit", "tool-call", "call_0_5")]),
                MockMessage([MockPart("", "tool-return", "call_0_5", "error")]),
                MockMessage(
                    [
                        MockPart("evaluate_code", "tool-call", "call_0_6"),
                        MockPart("run_pytest_test_code", "tool-call", "call_1_7"),
                    ]
                ),
                MockMessage(
                    [
                        MockPart(
                            "", "tool-return", "call_0_6", "Code executed successfully."
                        ),
                        MockPart(
                            "",
                            "tool-return",
                            "call_1_7",
                            "4 passed",
                            timestamp=datetime(2025, 2, 23, 20, 17, 35),
                        ),
                    ]
                ),
            ],
            "data": "The calculator agent has been successfully created and tested.",
        },
    )()

    score, cycles, coverage, tool_usage = evaluate_run_result(
        mock_run_result, max_tools=7
    )
    print(f"Score: {score}")
    print(f"Number of Cycles: {cycles}")
    print(f"Coverage: {coverage}")
    print(f"Tool Usage: {tool_usage}")
