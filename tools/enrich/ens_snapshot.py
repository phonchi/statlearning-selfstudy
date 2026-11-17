"""把上游各層跑完、尚未經 ensemble_deepen 的 BODIES 與 PAGEJS 存成 JSON（只供開發與預覽）。

用法：python3 tools/enrich/ens_snapshot.py  → tools/verification/ensemble-deepen-20261117/consult/old_bodies.json
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
os.environ["ENS_SKIP"] = "1"
import enrich_trees as T  # noqa: E402  （import 只跑各層，不寫 HTML）

OUT = HERE.parent / "verification/ensemble-deepen-20261117/consult/old_bodies.json"
OUT.write_text(json.dumps({"BODIES": T.BODIES, "PAGEJS": T.PAGEJS, "FRAMES": T.frames()}, ensure_ascii=False), encoding="utf-8")
print(OUT, len(T.BODIES), "節")
