"""The handled path. Twenty four cases.

Every case attaches an error_handler to the failing node. The declared policy
says the handler absorbs the error and the graph finishes. So PASS means no
exception escaped.

Solo and parallel, crossed with invoke, four streaming modes and two subgraph
shapes, each run synchronously and asynchronously.
"""

import asyncio

from _graphs import INPUT, build

MODES = ("values", "updates", "custom", "messages")


async def _acollect(graph, **kwargs):
    return [event async for event in graph.astream(INPUT, **kwargs)]


def _cases(graph):
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


def run():
    """Return [(label, passed, detail)]. Passed means the error did not escape."""
    results = []
    for parallel in (False, True):
        kind = "parallel" if parallel else "solo"
        graph = build(parallel=parallel, with_handler=True)
        for shape, call in _cases(graph):
            label = f"{kind:8} | {shape}"
            try:
                call()
                results.append((label, True, "no exception"))
            except Exception as exc:
                results.append((label, False, f"raised {type(exc).__name__}"))
    return results
