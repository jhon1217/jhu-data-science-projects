"""Validate local portfolio links and published project data."""

from __future__ import annotations

import json
import math
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.links.append(value)
            if key == "id" and value:
                self.ids.append(value)


def check_local_links() -> None:
    missing: list[str] = []
    bad_fragments: list[str] = []
    duplicate_ids: list[str] = []
    for page in ROOT.rglob("*.html"):
        if "tmp" in page.parts:
            continue
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8", errors="ignore"))
        repeated = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
        duplicate_ids.extend(f"{page.relative_to(ROOT)} -> #{item}" for item in repeated)
        for link in parser.links:
            parsed = urlsplit(link)
            if link.startswith("#"):
                fragment = unquote(parsed.fragment)
                if fragment and fragment not in parser.ids:
                    bad_fragments.append(f"{page.relative_to(ROOT)} -> {link}")
                continue
            if parsed.scheme or link.startswith(("mailto:", "tel:")):
                continue
            target = (page.parent / unquote(parsed.path)).resolve()
            if parsed.path.endswith("/"):
                target /= "index.html"
            if not target.exists():
                missing.append(f"{page.relative_to(ROOT)} -> {link}")
    assert not missing, "Missing local links:\n" + "\n".join(missing)
    assert not bad_fragments, "Missing page fragments:\n" + "\n".join(bad_fragments)
    assert not duplicate_ids, "Duplicate HTML ids:\n" + "\n".join(duplicate_ids)


def assert_close(actual: float, expected: float, digits: int) -> None:
    assert round(actual, digits) == round(expected, digits), f"Expected {expected}, got {actual}"


def check_project_data() -> None:
    cmapss = json.loads((ROOT / "projects/google-advanced/cmapss/data.json").read_text(encoding="utf-8"))
    assert cmapss["metrics"]["training_rows"] == 20631
    assert cmapss["metrics"]["training_engines"] == 100
    assert cmapss["metrics"]["test_engines"] == 100
    assert len(cmapss["predictions"]) == 100
    assert cmapss["source"]["subset"] == "FD001"

    predictions = cmapss["predictions"]
    engines = [row["engine"] for row in predictions]
    assert engines == list(range(1, 101)), "C-MAPSS test engines must be unique and ordered 1–100"
    for row in predictions:
        assert_close(row["error"], abs(row["predicted"] - row["actual"]), 1)
    rmse = math.sqrt(sum((row["predicted"] - row["actual"]) ** 2 for row in predictions) / len(predictions))
    mae = sum(abs(row["predicted"] - row["actual"]) for row in predictions) / len(predictions)
    within_20 = sum(row["error"] <= 20 for row in predictions) / len(predictions)
    assert_close(rmse, cmapss["metrics"]["official_test_rmse"], 2)
    assert_close(mae, cmapss["metrics"]["official_test_mae"], 2)
    assert_close(within_20, cmapss["metrics"]["within_20_cycles"], 3)
    assert 0 <= cmapss["metrics"]["validation_r2"] <= 1

    for engine, trajectory in cmapss["trajectories"].items():
        assert int(engine) in engines
        cycles = trajectory["cycle"]
        assert cycles == sorted(cycles) and len(cycles) == len(set(cycles))
        assert cycles, f"Engine {engine} trajectory is empty"
        for series_name, values in trajectory["series"].items():
            assert len(values) == len(cycles), f"Engine {engine} {series_name} length mismatch"

    divvy = json.loads((ROOT / "projects/google-data-analytics/divvy/data.json").read_text(encoding="utf-8"))
    totals = {row["user_type"]: row["trips"] for row in divvy["totals"]}
    assert totals == {"Customer": 880637, "Subscriber": 2937367}
    assert sum(totals.values()) == 3818004
    assert divvy["source"]["period"] == "2019"

    expected_shapes = {"monthly": 12, "weekday": 7, "hourly": 24}
    for dataset_name, expected_buckets in expected_shapes.items():
        rows = divvy[dataset_name]
        assert len(rows) == expected_buckets * 2
        for rider_type, total in totals.items():
            segment = [row for row in rows if row["user_type"] == rider_type]
            assert len(segment) == expected_buckets
            assert sum(row["trips"] for row in segment) == total, f"{dataset_name} does not reconcile for {rider_type}"

    assert {row["month"] for row in divvy["monthly"]} == set(range(1, 13))
    assert {row["weekday"] for row in divvy["weekday"]} == set(range(7))
    assert {row["hour"] for row in divvy["hourly"]} == set(range(24))
    assert all(60 <= row["avg_duration"] <= 86400 for row in divvy["monthly"])
    member_share = totals["Subscriber"] / sum(totals.values())
    assert round(member_share * 100) == 77

    for rider_type, total in totals.items():
        station_sum = sum(row["trips"] for row in divvy["top_stations"] if row["user_type"] == rider_type)
        assert 0 < station_sum <= total

    capstone = json.loads((ROOT / "capstone-results.json").read_text(encoding="utf-8"))
    corpus = capstone["corpus"]
    assert sum(source["lines"] for source in corpus.values()) == 4_269_678
    assert sum(source["words"] for source in corpus.values()) == 101_215_624
    validation = capstone["validation"]
    assert validation["tokens"] == 193_477
    assert sum(validation["backoff_orders"].values()) == validation["tokens"]
    assert_close(validation["top1_accuracy"] * 100, 12.44, 2)
    assert_close(validation["top3_accuracy"] * 100, 20.07, 2)
    assert validation["top1_accuracy"] <= validation["top3_accuracy"]
    assert all(capstone["example_predictions"].values())


def check_published_artifacts() -> None:
    required = {
        "practical-machine-learning.html": 100_000,
        "data-products-leaflet.html": 1_500,
        "data-products-plotly.html": 2_000,
        "data-products-shiny-pitch.html": 1_200,
        "capstone-pitch.html": 1_200,
        "capstone-milestone.html": 20_000,
        "reproducible-research-project-1.html": 100_000,
        "noaa-storm-analysis.pdf": 10_000,
        "regression-models-project.pdf": 10_000,
        "statistical-inference-project.pdf": 10_000,
    }
    for filename, minimum_size in required.items():
        artifact = ROOT / filename
        assert artifact.exists(), f"Missing published artifact: {filename}"
        assert artifact.stat().st_size >= minimum_size, f"Published artifact is unexpectedly small: {filename}"
        if artifact.suffix == ".pdf":
            assert artifact.read_bytes().startswith(b"%PDF"), f"Invalid PDF header: {filename}"
        else:
            head = artifact.read_text(encoding="utf-8", errors="ignore")[:20_000].lower()
            assert "<html" in head and "<title" in head, f"Invalid HTML document: {filename}"


def check_presentation_metrics() -> None:
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    cmapss_js = (ROOT / "projects/google-advanced/cmapss/dashboard.js").read_text(encoding="utf-8")
    divvy_js = (ROOT / "projects/google-data-analytics/divvy/dashboard.js").read_text(encoding="utf-8")
    for expected in ["19.77", "3.8 million", "100 test engines", 'data-project-count']:
        assert expected in index, f"Landing page is missing expected result: {expected}"
    assert "official_test_rmse" in cmapss_js and "official_test_mae" in cmapss_js
    assert "within_20_cycles" in cmapss_js and "training_rows" in cmapss_js
    assert all(token in divvy_js for token in ["data.totals", "data.monthly", "data.weekday", "data.hourly", "data.top_stations"])
    assert re.search(r"member\s*/\s*total\s*\*\s*100", divvy_js)

    capstone_pitch = (ROOT / "capstone-pitch.html").read_text(encoding="utf-8")
    milestone = (ROOT / "capstone-milestone.html").read_text(encoding="utf-8")
    for expected in ["4,269,678", "193,477", "12.44%", "20.07%"]:
        assert expected in capstone_pitch, f"Capstone pitch is missing validated result: {expected}"
        assert expected in milestone, f"Capstone milestone is missing validated result: {expected}"

    for app_name in ["capstone-app.R", "data-products-shiny-app.R"]:
        app = (ROOT / app_name).read_text(encoding="utf-8")
        assert "shinyApp(" in app, f"Incomplete Shiny application: {app_name}"
        assert 'source("ui.R"' not in app and 'source("server.R"' not in app, f"Missing split app files: {app_name}"


def main() -> None:
    check_local_links()
    check_project_data()
    check_published_artifacts()
    check_presentation_metrics()
    print("Portfolio checks passed: links, artifacts, chart series, and published metrics are valid.")


if __name__ == "__main__":
    main()
