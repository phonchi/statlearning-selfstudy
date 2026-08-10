"""共用路徑。所有腳本都從這裡取，不要在別處硬寫路徑。"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 課程 repo（講義 PDF 與中文 lab notebook 的來源）
COURSE = Path(os.environ.get("M524_COURSE", Path.home() / "nsysu-math524-2025"))
DECKS = COURSE / "static_files" / "presentations"
LECTURES = COURSE / "_lectures"

# 課本 PDF
BOOKS = Path(os.environ.get("M524_BOOKS", Path.home() / "statslearning"))
ISLP_PDF = BOOKS / "ISLP_website.pdf"
ESL_PDF = BOOKS / "ESLII_print12.pdf"

# 產出
SRC_INDEX = ROOT / "data" / "source_index"
FLASHCARDS = ROOT / "data" / "flashcards_zh"
QUESTIONS = ROOT / "data" / "questions_zh"
TEMPLATE = ROOT / "tools" / "template"


def require(p: Path, what: str) -> Path:
    if not p.exists():
        raise SystemExit(
            f"找不到{what}：{p}\n"
            f"設環境變數 M524_COURSE / M524_BOOKS 指到正確位置，或先 clone 課程 repo："
            f"\n  gh repo clone phonchi/nsysu-math524-2025 ~/nsysu-math524-2025"
        )
    return p
