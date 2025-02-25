import meta_loop


def build_agent(input_text: str, probe_count: int = 16, framework: str = "crewai"):
    """
    Build and optimize an agent based on the provided input text.
    """
    best_agent = meta_loop.build_agent(
        input_text=input_text, probe_count=probe_count, framework=framework
    )
    return best_agent


def custom_evaluation(trial: meta_loop.Trial) -> float:
    """
    Custom evaluation function for scoring probes.
    """
    # Implement custom evaluation logic here
    return 0.0  # Placeholder


def build_agent_with_custom_eval(
    input_text: str, probe_count: int = 16, framework: str = "crewai"
):
    """
    Build an agent using a custom evaluation function.
    """
    best_agent = meta_loop.build_agent(
        input_text=input_text,
        probe_count=probe_count,
        framework=framework,
        eval_fn=custom_evaluation,
    )
    return best_agent


def build_agent_with_dataset(
    input_text: str, probe_count: int = 16, framework: str = "crewai"
):
    """
    Build an agent with a test dataset.
    """
    test_dataset = meta_loop.dataset(
        ("Great product, love it!", 0.9),
        ("Terrible service, very disappointed.", 0.2),
        ("It's okay, nothing special.", 0.5),
    )
    best_agent = meta_loop.build_agent(
        input_text=input_text,
        probe_count=probe_count,
        framework=framework,
        test_dataset=test_dataset,
    )
    return best_agent
