"""Graph builders shared by both populations.

One failing node. Optionally a sibling in the same superstep, which is what
changes the task count inside the runner. The handler is attached or not
attached depending on which population is being measured.
"""

import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class S(TypedDict):
    log: Annotated[list, operator.add]


def boom(state):
    raise RuntimeError("boom from node")


def fine(state):
    return {"log": ["fine"]}


def handler(state):
    return Command(update={"log": ["handled"]}, goto=END)


def build(parallel: bool, with_handler: bool):
    g = StateGraph(S)
    kwargs = {"error_handler": handler} if with_handler else {}
    g.add_node("boom", boom, **kwargs)
    g.add_edge(START, "boom")
    if parallel:
        g.add_node("fine", fine)
        g.add_edge(START, "fine")
    return g.compile()


INPUT = {"log": []}
