"""The handled path. Twenty four cases on LangGraph.

Every case attaches the framework's declared error handler to the failing step.
The declared policy says the handler absorbs the error and execution finishes.
So PASS means no exception escaped.

Framework agnostic since 2026-09-04. The execution shapes moved into the
adapter, which is where the framework nouns belong. This file now holds one
thing: the assertion DIRECTION. Handled path asserts no escape.

DO NOT merge this with controls.py behind a flag. The two populations assert
OPPOSITE things, and a shared helper with an expect_raise parameter is how a
control quietly becomes a copy of the thing it is controlling.
"""

import adapters

ADAPTER = adapters.load()


def run():
    """Return [(label, passed, detail)]. Passed means the error did not escape."""
    results = []
    for parallel in (False, True):
        kind = "parallel" if parallel else "solo"
        graph = ADAPTER.build(parallel=parallel, with_handler=True)
        for shape, call in ADAPTER.shapes(graph):
            label = f"{kind:8} | {shape}"
            try:
                call()
                results.append((label, True, "no exception"))
            except Exception as exc:
                results.append((label, False, f"raised {type(exc).__name__}"))
    return results
