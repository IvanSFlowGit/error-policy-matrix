"""Framework adapters.

An adapter answers three questions about ONE framework and nothing else:

  NAME              what to call it in the report
  build(parallel, with_handler)   give me a runnable thing with one failing step
  shapes(thing)     every execution shape the framework offers, as (label, callable)
  control_shapes(thing)  the subset used for the over-suppression control

Everything above the adapter is framework agnostic and already was. run.py never
knew what it was testing, and matrix.py and controls.py only knew because the
execution shapes were written inline. Moving those into the adapter is the whole
extraction: no assertion changed, no label changed, no result changed.

WHY A SECOND ADAPTER IS THE POINT. One adapter is a bug report about one
framework. Two is a question anybody can ask of their own stack, and a framework
that behaves consistently across every shape is a publishable result too.
"""

import importlib

DEFAULT = "langgraph"


def load(name: str = DEFAULT):
    """Import an adapter by name. Refuses loudly rather than falling back.

    A missing adapter is a fixture failure and must not read as a framework
    result, which is the same rule run.py applies with its third exit code.
    """
    try:
        return importlib.import_module(f"adapters.{name}")
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            f"no adapter named {name!r} in adapters/. "
            f"This is a fixture failure, not a measurement."
        ) from exc
