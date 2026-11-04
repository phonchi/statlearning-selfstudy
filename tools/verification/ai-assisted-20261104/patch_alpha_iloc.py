"""Make cell 53 alpha_func use .iloc, matching boot_SE's positional draws."""
import json, sys
path = sys.argv[1]
nb = json.loads(open(path, encoding="utf-8").read())
src = nb["cells"][53]["source"]
old = "   cov_ = np.cov(D[['X','Y']].loc[idx], rowvar=False)\n"
assert src.count(old) == 1, src
src[src.index(old)] = "   cov_ = np.cov(D[['X','Y']].iloc[idx], rowvar=False)  # idx 是列的位置\n"
open(path, "w", encoding="utf-8").write(json.dumps(nb, ensure_ascii=False, separators=(",", ":")))
print("cell 53 patched")
