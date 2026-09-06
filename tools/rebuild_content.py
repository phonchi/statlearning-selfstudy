#!/usr/bin/env python3
"""Rebuild prose/JS from enrich sources, retaining current baked FRAMES verbatim.

For editorial changes only. To change model data, run the normal enrich script
and its pinned generator instead. Missing baked data is an error, not a fallback.
Usage: python3 tools/rebuild_content.py [page_stem ...]
"""
import ast
import json
import re
import sys
from pathlib import Path

from paths import ROOT


def frame_declarations(text):
    declarations = []
    for match in re.finditer(r"(?m)^const\s+(FRAMES_\w+)\s*=\s*", text):
        _, length = json.JSONDecoder().raw_decode(text[match.end():])
        declarations.append(text[match.start():match.end()+length] + ";")
    return "\n".join(declarations)


class KeepFrames(ast.NodeTransformer):
    def __init__(self, declarations):
        self.declarations = declarations

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "frames":
            if not self.declarations:
                raise ValueError("Existing page has no baked FRAMES; run the normal generator first")
            return ast.copy_location(ast.Constant(self.declarations), node)
        return self.generic_visit(node)


def rebuild(stems):
    enrich = ROOT / "tools" / "enrich"
    sys.path.insert(0, str(enrich))
    registry = {}
    for script in sorted(enrich.glob("enrich_*.py")):
        tree = ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        names = {n.args[0].value for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "apply" and n.args
                 and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)}
        if len(names) != 1:
            raise ValueError(f"Expected one literal apply() target in {script.name}: {names}")
        registry[names.pop()] = (script, tree)
    for stem in stems or registry:
        script, tree = registry[stem]
        existing = (ROOT / f"{stem}.html").read_text(encoding="utf-8")
        tree = ast.fix_missing_locations(KeepFrames(frame_declarations(existing)).visit(tree))
        exec(compile(tree, str(script), "exec"), {"__name__": "__main__", "__file__": str(script)})


if __name__ == "__main__":
    rebuild(sys.argv[1:])
