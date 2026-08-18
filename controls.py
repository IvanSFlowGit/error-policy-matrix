"""The over-suppression control. Six cases.

No error_handler anywhere. Nothing has been asked to absorb anything, so the
exception MUST reach the caller. PASS means it did.

These are not optional and they are the reason the twenty four are worth
reading. A change that stops the leak by suppressing everything turns the
handled path green and turns these red. A fixture that can only pass has not
been tested, it has only been run.
"""

import asyncio

from _graphs import INPUT, build


async def _acollect(graph, **kwargs):
    return [event async for event in graph.astream(INPUT, **kwargs)]


def _cases(graph):
    yield "invoke", lambda: graph.invoke(INPUT)
    yield "ainvoke", lambda: asyncio.run(graph.ainvoke(INPUT))
    yield "stream(custom)", lambda: list(graph.stream(INPUT, stream_mode="custom"))


def run():
    """Return [(label, passed, detail)]. Passed means the error DID escape."""
    results = []
    for parallel in (False, True):
        kind = "parallel" if parallel else "solo"
        graph = build(parallel=parallel, with_handler=False)
        for shape, call in _cases(graph):
            label = f"{kind:8} | {shape} (no handler)"
            try:
                call()
                results.append((label, False, "no exception, LEAKED SILENTLY"))
            except Exception as exc:
                results.append((label, True, f"raised {type(exc).__name__}"))
    return results
