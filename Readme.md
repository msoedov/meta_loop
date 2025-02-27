
<p align="center"> <h1 align="center">Meta Loop</h1> <p align="center"> An automatic agent optimization framework for generating, evaluating, and selecting top-performing agents.<br /> Define your task, and let Meta Loop discover the perfect solution.<br /> <a href="#">Explore the Docs »</a> · <a href="#">Report a Bug »</a> </p> </p> <p align="center"> <a href="#"> <img alt="GitHub Last Commit" src="https://img.shields.io/github/last-commit/msoedov/meta_loop?style=for-the-badge&logo=git&labelColor=000000&color=6A35FF" /> </a> <a href="#"> <img alt="GitHub Repo Size" src="https://img.shields.io/github/repo-size/msoedov/meta_loop?style=for-the-badge&logo=database&labelColor=000000&color=yellow" /> </a> <a href="#"> <img alt="GitHub License" src="https://img.shields.io/github/license/msoedov/meta_loop?style=for-the-badge&logo=codeigniter&labelColor=000000&color=FFCC19" /> </a> <a href="https://pypi.org/project/meta_loop/"> <img alt="PyPI Version" src="https://img.shields.io/pypi/v/meta_loop?style=for-the-badge&logo=pypi&labelColor=000000&color=00CCFF" /> </a> </p>

Meta Agent is a powerful, imperative, define-by-run framework designed to simplify agent development. It generates 16 candidate "probes" with varied configurations, evaluates them against customizable metrics, and selects the best-performing agent for your task. Whether you're analyzing data, predicting outcomes, or automating workflows, Meta Loop optimizes the process for you.
## ✨ Features

- Automated Agent Generation
- Creates 16 unique agent "probes" with diverse configurations tailored to your task.
- Customizable Evaluation
- Scores probes using built-in metrics (e.g., accuracy, speed) or your own custom evaluation function.
- Framework Flexibility
- Built with Pydantic-AI by default, with seamless support for frameworks like AutoGen or CrewAI.
- Extensible Design
- Easily adapt agent roles, tools, and evaluation criteria to suit your specific needs.


## 📦 Installation

Install Meta Agent with a single command:
```shell
pip install meta_loop

```
## 🚀 Quick Start

Get started in just a few lines of code. Below are examples to showcase Meta Agent’s capabilities.
Basic Usage

Generate an agent to analyze customer reviews and predict sentiment:
```python
import meta_loop

# Build and optimize an agent
best_agent = meta_loop.build_agent(
    instruction="Create an agent to analyze customer reviews and predict sentiment.",
    probe_count=16,
    framework="crewai"
)

# View the selected agent's details
print(best_agent.details)
```
### Custom Evaluation Function

Define your own scoring logic to evaluate probes:
```python
import meta_loop
import random

# Custom evaluation function
def custom_eval(trial: meta_loop.Trial) -> float:
    return random.random()  # Replace with your own metric

# Build an agent with custom evaluation
best_agent = meta_loop.build_agent(
    instruction="Create an agent to analyze customer reviews and predict sentiment.",
    probe_count=16,
    framework="crewai",
    eval_fn=custom_eval
)

print(best_agent.details)
```
### Using a Test Dataset

Provide a dataset to evaluate agents against specific inputs and expected outputs:
```python
import meta_loop

# Build an agent with a test dataset
best_agent = meta_loop.build_agent(
    instruction="Create an agent to analyze customer reviews and predict sentiment.",
    probe_count=16,
    framework="crewai",
    test_dataset=meta_loop.dataset(
        ("Great product, love it!", 0.9),  # (input, expected_score)
        ("Terrible service, very disappointed.", 0.2),
        ("It's okay, nothing special.", 0.5)
    )
)

print(best_agent.details)
```

## 🛠️ How It Works

- Define Your Task: Provide a task description (e.g., "analyze customer reviews").
- Generate Probes: Meta Agent creates 16 agent configurations with varying parameters.
- Evaluate Performance: Each probe is scored based on your chosen metrics or dataset.
- Select the Best: The top-performing agent is returned, ready for use.

## 📚 Documentation

For more details, check out the official documentation (coming soon!).
## 🤝 Contributing

We welcome contributions! Please see our contribution guidelines and feel free to submit issues or pull requests.

## 📬 Get in Touch

Have questions? Join our community or reach out:

- Discord (coming soon!)
- GitHub Issues
