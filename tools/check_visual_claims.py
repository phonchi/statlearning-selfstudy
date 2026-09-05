#!/usr/bin/env python3
"""Focused invariants for visuals that previously carried misleading claims.

This complements validate.py/browser_check.js: it checks source-level provenance and
the small number of numerical/causal invariants that rendering alone cannot catch.
"""
import ast
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENRICH = ROOT / "tools" / "enrich"
ALLOWED = {"course-data", "book-redraw", "simulation", "illustrative"}
FAIL = []


def fail(where, message):
    FAIL.append(f"[{where}] {message}")


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


# Every remaining viz() must make its source boundary explicit.
for path in sorted([*ENRICH.glob("enrich_*.py"), *ENRICH.glob("intro_visuals.py")]):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for call in (n for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "viz"):
        kw = next((k for k in call.keywords if k.arg == "provenance"), None)
        if kw is None:
            fail(path.name, f"viz() at line {call.lineno} has no provenance")
            continue
        try:
            kind, detail = ast.literal_eval(kw.value)
        except Exception:
            fail(path.name, f"viz() at line {call.lineno} provenance is not a literal pair")
            continue
        if kind not in ALLOWED or not str(detail).strip():
            fail(path.name, f"viz() at line {call.lineno} has invalid provenance {kind!r}")


# Removed hard-coded stories must not return.
for file, pattern, note in [
    ("tools/enrich/enrich_p6_modeling_api.py", r"22\.9（假的）|25\.6（真的）",
     "unsourced leakage MSE"),
    ("tools/enrich/enrich_deeplearning.py", r"a\s*=\s*-a\s*-\s*0\.4|w11seqSents",
     "hand-written sentiment rule presented as an RNN"),
    ("tools/enrich/enrich_svm.py", r"w10ovoSvg|大約 7%",
     "dataset-specific OVO/OVA percentage"),
    ("tools/frames/gen_svm.py", r"FRAMES_w10mc|make_blobs",
     "unused synthetic multiclass frames"),
    ("tools/enrich/enrich_modelsel.py", r"Math\.abs\([^\n]+\)\s*<\s*0\.005",
     "numeric threshold presented as exact Lasso sparsity"),
    ("tools/enrich/enrich_nonlin.py", r"w08knotR3",
     "spline reset points at a non-existent radio id"),
]:
    if re.search(pattern, source(file)):
        fail(file, note)


# Anscombe's quartet: all four plotted sets share the advertised summaries.
p5 = source("tools/enrich/enrich_p5_visualization.py")
mx = re.search(r"const w18smX = (\[[^;]+\]);", p5)
my = re.search(r"const w18smData = (\[.*?\n\]);", p5, re.S)
if not (mx and my):
    fail("P5", "cannot find Anscombe data literals")
else:
    xs0 = ast.literal_eval(mx.group(1))
    ysets = ast.literal_eval(my.group(1))
    xsets = [xs0, xs0, xs0, [8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8]]
    def mean(x): return sum(x) / len(x)
    def sd(x):
        m = mean(x)
        return math.sqrt(sum((v - m) ** 2 for v in x) / (len(x) - 1))
    def corr(x, y):
        a, b = mean(x), mean(y)
        return sum((u-a)*(v-b) for u, v in zip(x, y)) / ((len(x)-1)*sd(x)*sd(y))
    for i, (xs, ys) in enumerate(zip(xsets, ysets), 1):
        got = (mean(xs), mean(ys), sd(xs), sd(ys), corr(xs, ys))
        want = (9.0, 7.5, 3.3166, 2.0316, 0.816)
        if any(abs(a-b) > 0.015 for a, b in zip(got, want)):
            fail("P5", f"Anscombe set {i} summaries differ: {got}")


# Misleading-axis example must derive all views from one data literal.
if "const w18msGroups" not in p5 or "const w18msVals = w18msGroups.map" not in p5:
    fail("P5", "axis and boxplot views are not visibly derived from one dataset")


# LDA/QDA toggle: sampling uses the requested distributions, not the fitted rule.
cls = source("tools/enrich/enrich_classification.py")
if "w04lda2Sample(mu1, r1i" not in cls or "w04lda2Sample(mu2, r2i" not in cls:
    fail("Classification", "LDA/QDA comparison does not keep the same sampled data")


# RBF controls: gamma sweep fixes C=1; C sweep fixes gamma=1.
svm_tree = ast.parse(source("tools/frames/gen_svm.py"))
cfg = None
for node in svm_tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "RBF_CFG"
                                            for t in node.targets):
        cfg = ast.literal_eval(node.value)
if cfg is None:
    fail("SVM", "RBF_CFG not found")
else:
    if any(row[0] != 1 for row in cfg[:3]):
        fail("SVM", "gamma comparison changes C")
    if any(cfg[i][1] != 1 for i in (3, 1, 4)):
        fail("SVM", "C comparison changes gamma")


if FAIL:
    print("\n".join("FAIL " + x for x in FAIL))
    raise SystemExit(1)
print("visual claim checks: OK")
