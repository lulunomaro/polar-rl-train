"""Semantic diff of two mjlab env-config YAML dumps (formatting-insensitive).

Usage: python scripts/diff_env_yaml.py <a.yaml> <b.yaml>
Prints one line per differing leaf/collection, capped at 120 lines.
"""
from __future__ import annotations

import sys

import yaml

shown = 0
LIMIT = 120


class Lenient(yaml.SafeLoader):
    """SafeLoader that tolerates !!python/... tags (enums, lambdas, tuples)."""


def _python_tag(loader, suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node, deep=True)
    return loader.construct_mapping(node, deep=True)


Lenient.add_multi_constructor("tag:yaml.org,2002:python/", _python_tag)


def emit(*parts: object) -> None:
    global shown
    if shown < LIMIT:
        print(*parts)
    shown += 1


def walk(x, y, path: str = "") -> None:
    if isinstance(x, dict) and isinstance(y, dict):
        for k in sorted(set(x) | set(y), key=str):
            if k not in x:
                emit("ONLY_IN_B", "%s/%s" % (path, k), repr(y[k])[:90])
            elif k not in y:
                emit("ONLY_IN_A", "%s/%s" % (path, k), repr(x[k])[:90])
            else:
                walk(x[k], y[k], "%s/%s" % (path, k))
        return
    if isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
        if len(x) != len(y):
            emit("LEN_DIFF", path, len(x), len(y))
            return
        for i, (xi, yi) in enumerate(zip(x, y)):
            walk(xi, yi, "%s[%d]" % (path, i))
        return
    if type(x) is not type(y) or x != y:
        emit("DIFF", path, repr(x)[:90], "!=", repr(y)[:90])


def main() -> int:
    a = yaml.load(open(sys.argv[1], encoding="utf8"), Loader=Lenient)
    b = yaml.load(open(sys.argv[2], encoding="utf8"), Loader=Lenient)
    walk(a, b)
    print("total differences:", shown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
