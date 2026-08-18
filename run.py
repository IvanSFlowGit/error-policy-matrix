"""Run both populations and report them separately.

Three outcomes, not two:

    0  PASS            every case executed and every assertion held
    1  FAIL            every case executed, at least one assertion did not
    2  COULD NOT RUN   import error, missing symbol, changed signature

Exit 2 is the one that matters when this is pointed at an unfamiliar build. A
fixture that cannot execute produces zero passes, and zero passes reads exactly
like a broken framework when the truth is a broken fixture.
"""

import sys
import traceback

COULD_NOT_RUN = 2


def _bail(what, exc):
    print(f"COULD NOT RUN: {what}")
    print()
    traceback.print_exception(type(exc), exc, exc.__traceback__)
    print()
    print("This is a fixture failure, not a measurement. Exit 2.")
    return COULD_NOT_RUN


def _report(title, results, expectation):
    print(title)
    print(f"  ({expectation})")
    print()
    for label, passed, detail in results:
        mark = "pass" if passed else "FAIL"
        print(f"  {mark:4}  {label:44} {detail}")
    passed_n = sum(1 for _, ok, _ in results if ok)
    print()
    print(f"  {passed_n} of {len(results)}")
    print()
    return passed_n, len(results)


def main():
    try:
        import controls
        import matrix
    except Exception as exc:
        return _bail("could not import the fixture modules", exc)

    try:
        handled = matrix.run()
        control = controls.run()
    except Exception as exc:
        return _bail("a case could not be constructed or executed", exc)

    print()
    h_pass, h_total = _report(
        "HANDLED PATH", handled, "an error routed to a handler must NOT escape"
    )
    c_pass, c_total = _report(
        "OVER-SUPPRESSION CONTROL",
        control,
        "an error with NO handler anywhere MUST escape",
    )

    print("SUMMARY")
    print(f"  handled path  {h_pass} of {h_total}")
    print(f"  control       {c_pass} of {c_total}")
    print()

    if h_pass == h_total and c_pass == c_total:
        print("PASS. Every case executed and every assertion held.")
        return 0

    if c_pass < c_total:
        print("FAIL, and the control is the one that broke.")
        print("An error with no handler is being suppressed. That is fail-open")
        print("and it is worse than the leak this fixture was written for.")
    else:
        print("FAIL. The handled path leaks on at least one execution shape.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
