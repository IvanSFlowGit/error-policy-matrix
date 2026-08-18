# langgraph-error-handler-matrix

A test matrix for one question: does a graph's declared error handling policy
produce the same terminal result across every execution shape it can be run in?

It exists because that answer turned out to be no. A handler can run, apply its
recovery and update state, and the original exception can still escape, depending
on whether the graph has parallel nodes and on which streaming mode is used. Same
declared policy, different effective semantics.

## What is in it

Thirty cases, and they are two different populations. Never quote a count without
saying which one it came from.

| set | cases | what it asserts |
|---|---|---|
| handled path | 24 | an error routed to a handler does NOT escape |
| over-suppression control | 6 | an error with NO handler anywhere DOES escape |

The 24 are solo and parallel crossed with invoke, four streaming modes and two
subgraph shapes, each run synchronously and asynchronously.

**The 6 are not optional and they are the reason the 24 are worth reading.** A
fixture that can only pass has not been tested, it has only been run. If a change
suppresses the leak by suppressing everything, the handled-path cases go green and
the controls go red. Both sets run on every invocation and the summary reports
them separately.

## Running it

There is no package and no installer. Four files and the standard library.

    git clone <repo-url>
    cd langgraph-error-handler-matrix
    python -m venv .venv && source .venv/bin/activate

Then install the framework at whatever build you want to measure, and run it.

    pip install langgraph==1.2.11        # or install from a git ref
    python run.py

Pointing it at a branch or a pull request means installing that build into the
environment yourself. **The fixture does not check out refs for you, and it does
not know what it is running against.** It measures whatever `import langgraph`
resolves to, so record the build separately.

Measured on Python 3.11.15 in a fresh virtual environment. A different base is
measuring something else.

### Three outcomes, not two

| exit | meaning |
|---|---|
| 0 | PASS. Every case executed and every assertion held. |
| 1 | FAIL. Every case executed and at least one assertion did not hold. |
| 2 | COULD NOT RUN. Import error, missing symbol, changed signature. |

**Exit 2 is the one that matters when you point this at your own branch.** A
fixture that cannot execute produces zero passes, and zero passes reads exactly
like a broken framework when the truth is a broken fixture. The summary names
which of the three it is, and how many cases in each set were reached.

All three exit states were exercised before publishing, including exit 2 against
a deliberately broken copy.

## What was measured, and when

These are results from named builds on a named date. They are **not** claims about
what the framework does now. Commits move, branches get force-pushed, and a result
stated without its build becomes false on its own the first time anybody merges
anything.

| build | identifier | handled path | control |
|---|---|---|---|
| release 1.2.11 | `644815f` | 6 of 24 pass | 6 of 6 still raise |
| PR #8611, head at time of run | `adfa8d0f` | 24 of 24 pass | 6 of 6 still raise |

First measured 16 August 2026 and re-run against a rebuilt fixture on 18 August
2026 with identical results.

**The first row is reproducible without resolving a commit.** `644815f` is the
release commit for 1.2.11, so `pip install langgraph==1.2.11` stands the baseline
up directly.

**On the second row, the pull request number is the durable identifier and the
commit is not.** `adfa8d0f` is the head of a branch on a fork. If it is
force-pushed the sha moves, and if the fork is deleted the sha becomes
unreachable.

**And the closure of that pull request carries no signal about the change.** It
was closed nineteen seconds after opening, by a workflow bot rather than a
reviewer:

> This PR has been automatically closed because you are not assigned to the linked
> issue. External contributors must be assigned to an issue before opening a PR
> for it.

No human read it. So 24 of 24 on its head is a measurement of a branch, and not an
endorsement of a change anybody has reviewed or adopted.

## Provenance

The defect was reported by the issue author, not by me. The change measured in the
second row is somebody else's work. This repository is the test matrix only.

Upstream thread: langchain-ai/langgraph issue 8608.

## The obvious extension, which is not built here

The general version of this is a harness that checks whether any declared error
handling policy holds across every execution shape a framework offers, rather than
this one policy in this one framework, and that resolves refs itself rather than
leaving the environment to you. That is a different project. It is named here so
nobody assumes this is it.

## Licence

MIT. See LICENSE.

LangGraph is MIT (Copyright (c) 2024 LangChain, Inc.), so this is compatible
upstream. Any file here containing code copied from the framework or from the
issue reproduction keeps the original copyright line in its own header.
