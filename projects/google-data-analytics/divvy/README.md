# Divvy Rider Behavior

Behavioral analysis of 2019 Chicago bike-share trips from the City of Chicago Data Portal.

## Question

How do casual customers and members differ across season, day, hour, trip duration, and origin station?

## Method

- Direct aggregate queries to the public data API
- Segment comparison across time and place
- Duration filtering for operational anomalies
- Recommendations tied to the strongest observed patterns

## Reproduce

Run the standard-library Python script:

```bash
python fetch_analysis.py
```

The script writes `data.json` for the interactive presentation.

**[Open the published case study](https://jhon1217.github.io/jhu-data-science-projects/projects/google-data-analytics/divvy/)**
