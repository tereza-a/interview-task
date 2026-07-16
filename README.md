# Code Review Task — Meter Ingestion Service

## What it does

Energy meters report **power (kW) every 30 minutes**. Once a day a device uploads
a batch of readings. The service stores it, converts the readings to **total
energy (kWh)**, appends the day's total to the device's history in **S3**,
compares it against a **billing service**, and alerts an operator on a mismatch.

Two short files:

- `app/api.py` — the FastAPI endpoint.
- `app/metrics.py` — helpers that turn power readings into energy figures.

It's **deliberately imperfect** — treat it like a pull request to review.

## Your task (~10 min)

We care about **how you think**, not an exhaustive list.

1. **Issues you'd flag** — with a quick *why* and *how serious*.
2. If you could fix only **three** first, which three and why?

No need to run or fix the code — just walk us through your review. Thinking out
loud is welcome; assume it's a real service under real traffic.
