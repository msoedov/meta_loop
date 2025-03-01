import asyncio
import os

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from meta_loop import primitives
from meta_loop.eval import evaluate_run_result
from meta_loop.utils import verbose_decorator

# Initialize the model
model = OpenAIModel(
    "deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=os.environ["DEEPSEEK_KEY"],
)


class Prompt(BaseModel):
    original: str
    optimized: str


async def prompt_refiner(prompt: str) -> Prompt:
    agent_creator = Agent(model, result_type=Prompt)
    result = await agent_creator.run(f"Refine prompt: {prompt}")
    print(result.data)
    return result.data


async def researcher(instruction: str, t: primitives.Trial):
    prompt = await prompt_refiner(instruction)
    print(prompt)


def builder(revision: str):
    agent_creator = Agent(model)

    # Tool to list available frameworks
    @agent_creator.tool
    @verbose_decorator
    def get_frameworks(ctx: RunContext[str]):
        """List all framework directories in 'kb'."""
        if not os.path.exists("kb"):
            return []
        return [f for f in os.listdir("kb") if os.path.isdir(os.path.join("kb", f))]

    @agent_creator.tool
    @verbose_decorator
    def get_allowed_tools(ctx: RunContext[str]):
        """List all framework directories in 'kb'."""
        if not os.path.exists("kb"):
            return []
        return [f for f in os.listdir("kb") if os.path.isdir(os.path.join("kb", f))]

    @agent_creator.tool
    @verbose_decorator
    def authorize_tool_usage(ctx: RunContext[str]):
        """List all framework directories in 'kb'."""
        if not os.path.exists("kb"):
            return []
        return [f for f in os.listdir("kb") if os.path.isdir(os.path.join("kb", f))]

    # Tool to list markdown files in a directory
    @agent_creator.tool
    @verbose_decorator
    def list_documentation_files(
        ctx: RunContext[str], directory_path: str
    ) -> list[str]:
        """List all .md and .mdx files in the specified directory."""
        if not os.path.exists(directory_path):
            return []
        return [
            os.path.join(directory_path, f)
            for f in os.listdir(directory_path)
            if f.endswith(".md") or f.endswith(".mdx")
        ]

    # Tool to read a file's content
    @agent_creator.tool
    @verbose_decorator
    def read_documentation_file(ctx: RunContext[str], file_path: str) -> str:
        """Read the content of a file if it exists."""
        if not os.path.exists(file_path):
            return f"No such file {file_path}"
        with open(file_path) as f:
            return f.read()

    # Tool to write code to a file
    @agent_creator.tool
    @verbose_decorator
    def write_code(ctx: RunContext[str], file_path: str, code: str):
        """Write the provided code to a file."""
        with open(file_path, "w") as f:
            f.write(code)

    # Tool to write test code to a file
    @agent_creator.tool
    @verbose_decorator
    def write_test_code(ctx: RunContext[str], file_path: str, code: str):
        """Write the provided test code to a file."""
        with open(file_path, "w") as f:
            f.write(code)

    @agent_creator.tool
    @verbose_decorator
    def create_agent_workdir(ctx: RunContext[str], agent_name: str):
        """Create a directory for the agent and return its path."""
        # Make multi revision results
        agent_dir = os.path.join("sandbox", revision, agent_name)
        if not os.path.exists(agent_dir):
            os.makedirs(agent_dir)
        return agent_dir

    # Tool to run pytest on a test file
    @agent_creator.tool
    @verbose_decorator
    def run_pytest_test_code(ctx: RunContext[str], file_path: str):
        """Run pytest on the specified test file and return the output."""
        import subprocess

        result = subprocess.run(["pytest", file_path], capture_output=True)
        return result.stdout.decode("utf-8")

    # Tool to evaluate code by executing it
    @agent_creator.tool
    @verbose_decorator
    def evaluate_code(ctx: RunContext[str], file_path: str):
        """Execute the code in the file and return any errors or success message."""
        if not os.path.exists(file_path):
            return f"No such file {file_path}"
        with open(file_path) as f:
            code = f.read()
        try:
            exec(code)
        except Exception as e:
            return str(e)
        return "Code executed successfully."

    @agent_creator.tool
    @verbose_decorator
    def run_pre_commit(ctx: RunContext[str]):
        """Run pre-commit checks on the code."""
        import subprocess

        result = subprocess.run(
            ["pre-commit", "run", "--all-files"], capture_output=True
        )
        return result.stdout.decode("utf-8")

    return agent_creator


# Track tools usage and evaluate steps heuristically


def revision_generator(n: int):
    for i in range(n):
        yield f"v{i}"


def build_agent(
    instruction,
    probe_count: int = 16,
    framework="*",
    eval_fn=None,
    test_dataset=None,
    **kwargs,
):
    """
    Build an agent based on the instruction.
    """

    async def main():
        # timeout = 5 * 60  # 2-minute timeout
        generations = []
        for revision in revision_generator(n=probe_count):
            agent = builder(revision)
            generations.append(agent)

        coroutines = []
        for agent_creator in generations:
            refined_instructions = await prompt_refiner(instruction)
            task = asyncio.create_task(
                agent_creator.run(refined_instructions.optimized)
            )
            coroutines.append(task)

        result = await asyncio.gather(*coroutines)
        print(result)
        metrics = evaluate_run_result(result)
        print(metrics)

    return asyncio.run(main())
