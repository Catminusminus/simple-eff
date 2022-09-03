# Simple Eff
A Simple Tiny (only <100 lines) Algebraic Effects Library for Python.

```python
from typing import Any, Callable, Generator, Optional

from simple_eff import Effect, eff, Eff

not_integer = Effect()


def parse_int(str: str) -> Optional[int]:
    try:
        return int(str)
    except Exception:
        return None


@eff
def sum_lines(s: str) -> Generator[Eff[str], int, int]:
    lines = s.split()
    sum = 0
    for line in lines:
        match parse_int(line):
            case None:
                sum += yield not_integer.perform(line)
            case num:
                sum += num
    return sum


def handle_notinteger(k: Callable, v: str) -> Any:
    print(f"Parse Error: {v} is not an integer.")
    return k(0)


if __name__ == "__main__":
    twelve = sum_lines("1\n2\nthree\n4\n5")
    twelve.on(not_integer, handle_notinteger)
    ret = twelve.run()
    print(f"Sum: {ret}")
```

## Acknowledgement
This library is ...
- inspired by [effective-rust](https://github.com/pandaman64/effective-rust) for the API design.
- heavily based on [ruff](https://github.com/Nymphium/ruff) for the implementation.
