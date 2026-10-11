"""Build the public Divvy 2019 case-study dataset from Chicago's open-data API."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENDPOINT = "https://data.cityofchicago.org/resource/fg6s-gzvg.json"
PERIOD = "start_time between '2019-01-01T00:00:00.000' and '2019-12-31T23:59:59.999'"
VALID_DURATION = "trip_duration between 60 and 86400"


def query(select: str, group: str = "", order: str = "", where: str = PERIOD) -> list[dict]:
    params = {"$select": select, "$where": where, "$limit": "5000"}
    if group:
        params["$group"] = group
    if order:
        params["$order"] = order
    url = ENDPOINT + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "portfolio-analysis/1.0"})
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.load(response)


def numeric(rows: list[dict], integer: tuple[str, ...] = ()) -> list[dict]:
    for row in rows:
        for key, value in list(row.items()):
            if key in integer:
                row[key] = int(float(value))
            elif key not in {"user_type", "from_station_name"}:
                row[key] = round(float(value), 2)
    return rows


def main() -> None:
    totals = numeric(
        query("user_type, count(*) as trips", group="user_type", order="user_type"),
        ("trips",),
    )
    monthly = numeric(
        query(
            "date_extract_m(start_time) as month, user_type, count(*) as trips, "
            "avg(trip_duration) as avg_duration",
            group="month,user_type",
            order="month,user_type",
            where=f"{PERIOD} and {VALID_DURATION}",
        ),
        ("month", "trips"),
    )
    weekday = numeric(
        query(
            "date_extract_dow(start_time) as weekday, user_type, count(*) as trips",
            group="weekday,user_type",
            order="weekday,user_type",
        ),
        ("weekday", "trips"),
    )
    hourly = numeric(
        query(
            "date_extract_hh(start_time) as hour, user_type, count(*) as trips",
            group="hour,user_type",
            order="hour,user_type",
        ),
        ("hour", "trips"),
    )
    top_stations = numeric(
        query(
            "from_station_name, user_type, count(*) as trips",
            group="from_station_name,user_type",
            order="trips desc",
        ),
        ("trips",),
    )

    output = {
        "source": {
            "name": "Divvy Trips",
            "publisher": "City of Chicago Data Portal",
            "url": "https://data.cityofchicago.org/Transportation/Divvy-Trips/fg6s-gzvg",
            "period": "2019",
        },
        "totals": totals,
        "monthly": monthly,
        "weekday": weekday,
        "hourly": hourly,
        "top_stations": top_stations,
        "method": {
            "duration_filter": "Average duration excludes trips shorter than 60 seconds or longer than 24 hours.",
            "refresh": "Aggregates generated directly from the City of Chicago Open Data API.",
        },
    }
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "data.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({row["user_type"]: row["trips"] for row in totals}, indent=2))


if __name__ == "__main__":
    main()
