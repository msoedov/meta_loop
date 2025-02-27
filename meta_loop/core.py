class Trial:
    """
    State of experiment.
    """

    def __init__(self, agent, dataset, eval_fn):
        self.agent = agent
        self.dataset = dataset
        self.eval_fn = eval_fn

    def run(self):
        return


def build_agent(
    instruction,
    probe_count: int = 16,
    framework="*",
    eval_fn=None,
    test_dataset=None,
    **kwargs
):
    """
    Build an agent based on the instruction.
    """
    return


def dataset(*pairs: tuple[str, float]):
    """
    Return the dataset.
    """
    return
