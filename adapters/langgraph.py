"""LangGraph adapter.

One failing node. Optionally a sibling in the same superstep, which is what
changes the task count inside the runner. The handler is attached or not
attached depending on which population is being measured.

This file holds every LangGraph noun in the project. stream_mode, subgraphs,
astream, StateGraph and Command appear here and nowhere else, so a second
framework is a second file beside this one rather than an edit to the runner.
"""

import asyncio

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


NAME = "langgraph"

# Every streaming mode the framework offers. A framework with one execution
# shape gives a one cell matrix, which is why this list is the adapter's job.
MODES = ("values", "updates", "custom", "messages")


async def _acollect(graph, **kwargs):
    return [event async for event in graph.astream(INPUT, **kwargs)]


def shapes(graph):
    """Every execution shape, as (label, callable). Twenty four with MODES=4.

    The labels are the report's labels and must not drift: they were chosen so a
    reader can see which shape leaked without reading the code.
    """
    yield "invoke", lambda: graph.invoke(INPUT)
    yield "ainvoke", lambda: asyncio.run(graph.ainvoke(INPUT))
    for mode in MODES:
        yield f"stream({mode})", lambda m=mode: list(graph.stream(INPUT, stream_mode=m))
        yield f"astream({mode})", lambda m=mode: asyncio.run(_acollect(graph, stream_mode=m))
    yield "stream(values, subgraphs)", lambda: list(
        graph.stream(INPUT, stream_mode="values", subgraphs=True)
    )
    yield "astream(custom, subgraphs)", lambda: asyncio.run(
        _acollect(graph, stream_mode="custom", subgraphs=True)
    )


def control_shapes(graph):
    """The control subset. Three shapes, deliberately fewer.

    The control asks a different question and does not need the full cross
    product to answer it: if an unhandled error escapes on invoke, ainvoke and
    one streaming mode, the runner is not swallowing errors generally.
    """
    yield "invoke", lambda: graph.invoke(INPUT)
    yield "ainvoke", lambda: asyncio.run(graph.ainvoke(INPUT))
    yield "stream(custom)", lambda: list(graph.stream(INPUT, stream_mode="custom"))
