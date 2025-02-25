import asyncio
import os
from functools import wraps

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

# Initialize the model
model = OpenAIModel(
    "deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=os.environ["DEEPSEEK_KEY"],
)


# Verbose decorator for logging tool execution
def verbose_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # run_context = args[0]
        pargs = args[1:]
        print(f"Running {func.__name__} with args {pargs} and kwargs {kwargs}")
        r = func(*args, **kwargs)
        print(f"Result: {r}")
        return r

    return wrapper


def build_agent(revision: str):
    agent_creator = Agent(model)

    # Tool to list available frameworks
    @agent_creator.tool
    @verbose_decorator
    def get_frameworks(ctx: RunContext[str]):
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


# Main execution function
async def main():
    # timeout = 5 * 60  # 2-minute timeout
    generations = []
    for revision in ["v1"]:
        # for revision in ["v1", "v2", "v3"]:
        agent = build_agent(revision)
        generations.append(agent)

    coroutines = []
    for agent_creator in generations:
        task = asyncio.create_task(
            agent_creator.run("Create me a calculator agent in pydantic-ai.")
        )
        coroutines.append(task)

    result = await asyncio.gather(*coroutines)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
