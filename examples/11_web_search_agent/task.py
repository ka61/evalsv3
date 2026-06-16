"""Example 11 — A research agent with web search.

A react agent that uses the web_search tool to answer open questions, graded by a
model. NOTE: web_search needs a search provider configured — some model providers
offer built-in search; others require an external provider/key. See the README.

Run:
    inspect eval examples/11_web_search_agent/task.py --model openrouter/openai/gpt-5.4
"""

from inspect_ai import Task, task
from inspect_ai.agent import react
from inspect_ai.dataset import Sample
from inspect_ai.scorer import model_graded_qa
from inspect_ai.tool import web_search


@task
def researcher():
    return Task(
        dataset=[
            Sample(
                input="What is the boiling point of water at sea level in Celsius?",
                target="100 degrees Celsius",
            ),
            Sample(
                input="In what year did the first iPhone go on sale?",
                target="2007",
            ),
        ],
        solver=react(tools=[web_search()]),
        scorer=model_graded_qa(),
    )
