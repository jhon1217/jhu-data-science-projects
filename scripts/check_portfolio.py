"""Validate local portfolio links and published project data."""

from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.links.append(value)


def check_local_links() -> None:
    missing: list[str] = []
    for page in ROOT.rglob("*.html"):
        if "tmp" in page.parts:
            continue
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8", errors="ignore"))
        for link in parser.links:
            parsed = urlsplit(link)
            if parsed.scheme or link.startswith(("#", "mailto:", "tel:")):
                continue
            target = (page.parent / unquote(parsed.path)).resolve()
            if parsed.path.endswith("/"):
                target /= "index.html"
            if not target.exists():
                missing.append(f"{page.relative_to(ROOT)} -> {link}")
    assert not missing, "Missing local links:\n" + "\n".join(missing)


def check_project_data() -> None:
    cmapss = json.loads((ROOT / "projects/google-advanced/cmapss/data.json").read_text(encoding="utf-8"))
    assert cmapss["metrics"]["training_rows"] == 20631
    assert cmapss["metrics"]["test_engines"] == 100
    assert len(cmapss["predictions"]) == 100

    divvy = json.loads((ROOT / "projects/google-data-analytics/divvy/data.json").read_text(encoding="utf-8"))
    totals = {row["user_type"]: row["trips"] for row in divvy["totals"]}
    assert totals == {"Customer": 880637, "Subscriber": 2937367}
    assert sum(totals.values()) == 3818004


def main() -> None:
    check_local_links()
    check_project_data()
    print("Portfolio checks passed: local links and project data are valid.")


if __name__ == "__main__":
    main()
