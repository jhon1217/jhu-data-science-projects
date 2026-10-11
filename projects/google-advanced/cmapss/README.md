# Predictive Maintenance: Jet Engine Remaining Useful Life

Machine learning case study using the NASA C-MAPSS FD001 subset.

## Question

Can multivariate sensor histories estimate the remaining useful life of an engine well enough to help prioritize maintenance attention?

## Method

- Capped remaining useful life target
- Sensor screening and rolling features
- Engine-level development holdout
- Random forest regression
- Evaluation on NASA's separate test fleet

## Reproduce

Install `numpy`, `pandas`, and `scikit-learn`, then run:

```bash
python build_analysis.py
```

The script retrieves the public source when needed and writes `data.json` for the interactive presentation.

**[Open the published case study](https://jhon1217.github.io/jhu-data-science-projects/projects/google-advanced/cmapss/)**
