import asyncio
import os
import subprocess

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
    api_key=os.environ.get("DEEPSEEK_KEY", ""),
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
        try:
            with open(file_path) as f:
                return f.read()
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"

    # Tool to write code to a file
    @agent_creator.tool
    @verbose_decorator
    def write_code(ctx: RunContext[str], file_path: str, code: str):
        """Write the provided code to a file."""
        try:
            with open(file_path, "w") as f:
                f.write(code)
            return f"Code written to {file_path}"
        except Exception as e:
            return f"Error writing to file {file_path}: {str(e)}"

    # Tool to write test code to a file
    @agent_creator.tool
    @verbose_decorator
    def write_test_code(ctx: RunContext[str], file_path: str, code: str):
        """Write the provided test code to a file."""
        try:
            with open(file_path, "w") as f:
                f.write(code)
            return f"Test code written to {file_path}"
        except Exception as e:
            return f"Error writing to file {file_path}: {str(e)}"

    @agent_creator.tool
    @verbose_decorator
    def create_agent_workdir(ctx: RunContext[str], agent_name: str):
        """Create a directory for the agent and return its path."""
        agent_dir = os.path.join("sandbox", revision, agent_name)
        try:
            os.makedirs(agent_dir, exist_ok=True)
            return agent_dir
        except Exception as e:
            return f"Error creating directory {agent_dir}: {str(e)}"

    # Tool to run pytest on a test file
    @agent_creator.tool
    @verbose_decorator
    def run_pytest_test_code(ctx: RunContext[str], file_path: str):
        """Run pytest on the specified test file and return the output."""
        try:
            result = subprocess.run(
                ["pytest", file_path], capture_output=True, check=True
            )
            return result.stdout.decode("utf-8")
        except subprocess.CalledProcessError as e:
            return f"Pytest failed with return code {e.returncode}: {e.stderr.decode('utf-8')}"
        except FileNotFoundError:
            return "Pytest is not installed or not found in PATH."
        except Exception as e:
            return f"Error running pytest: {str(e)}"

    # Tool to evaluate code by executing it
    @agent_creator.tool
    @verbose_decorator
    def evaluate_code(ctx: RunContext[str], file_path: str):
        """Execute the code in the file and return any errors or success message."""
        if not os.path.exists(file_path):
            return f"No such file {file_path}"
        try:
            result = subprocess.run(
                ["python", file_path], capture_output=True, check=True
            )
            return result.stdout.decode("utf-8")
        except subprocess.CalledProcessError as e:
            return f"Code execution failed: {e.stderr.decode('utf-8')}"
        except FileNotFoundError:
            return "Python interpreter not found."
        except Exception as e:
            return f"Error executing code: {str(e)}"

    @agent_creator.tool
    @verbose_decorator
    def run_pre_commit(ctx: RunContext[str]):
        """Run pre-commit checks on the code."""
        try:
            result = subprocess.run(
                ["pre-commit", "run", "--all-files"], capture_output=True, check=True
            )
            return result.stdout.decode("utf-8")
        except subprocess.CalledProcessError as e:
            return f"Pre-commit failed: {e.stderr.decode('utf-8')}"
        except FileNotFoundError:
            return "Pre-commit is not installed or not found in PATH."
        except Exception as e:
            return f"Error running pre-commit: {str(e)}"

    return agent_creator


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
    Build and run multiple agents based on the instruction, refining prompts in parallel.

    Args:
        instruction (str): The initial instruction for the agents.
        probe_count (int): Number of agent instances to create (default: 16).
        framework (str): Framework filter (default: "*").
        eval_fn (callable, optional): Custom evaluation function.
        test_dataset (Any, optional): Dataset for testing.
        **kwargs: Additional keyword arguments.
    """

    async def main():
        # Create agent instances for each revision
        generations = [
            builder(revision) for revision in revision_generator(n=probe_count)
        ]

        # Parallelize prompt refinements
        refinement_tasks = [prompt_refiner(instruction) for _ in range(probe_count)]
        refined_prompts = await asyncio.gather(*refinement_tasks)

        # Create tasks for running agents with refined prompts
        coroutines = []
        for agent_creator, refined in zip(generations, refined_prompts):
            task = asyncio.create_task(agent_creator.run(refined.optimized))
            coroutines.append(task)

        # Gather results, capturing exceptions
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                print(f"Task failed with exception: {result}")
            else:
                print(f"Task succeeded: {result}")

        # Evaluate the results
        metrics = evaluate_run_result(results)
        print(metrics)

    return asyncio.run(main())
