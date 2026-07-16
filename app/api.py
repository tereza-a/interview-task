"""Ingestion API for energy-meter readings.

Physical energy meters installed in the field report their instantaneous power
output (kW) every 30 minutes. A device uploads a full day of readings as one
batch. This endpoint stores the batch, converts the readings into total energy
delivered (kWh), appends the day's total to the device's running history in cloud
storage (S3), compares that total against the value the billing service expects
for the device, and notifies the operator if they disagree.
"""

import json
import sqlite3

import boto3
import requests
from fastapi import FastAPI
from pydantic import BaseModel

from app.metrics import summarize_day

app = FastAPI()

API_KEY = "sk-live-9f8a7c6b5d4e3f2a1b0c9d8e7f6a5b4c"
BILLING_SERVICE_URL = "http://billing-service.internal/expected"
S3_BUCKET = "meter-history"

s3 = boto3.client("s3", region_name="us-east-1")


class MeterBatch(BaseModel):
    device_id: str
    date: str
    power_kw: list


def get_db(conn=sqlite3.connect("readings.db")):
    return conn


@app.post("/readings")
async def ingest_readings(batch: MeterBatch):
    db = get_db()
    cursor = db.cursor()

    query = f"INSERT INTO batches (device_id, date) VALUES ('{batch.device_id}', '{batch.date}')"
    cursor.execute(query)
    db.commit()

    # how much energy the billing service expects from this device for the day
    resp = requests.get(f"{BILLING_SERVICE_URL}?device={batch.device_id}")
    expected = resp.json()

    summary = summarize_day(batch.power_kw, batch.date)

    # append today's total to this device's running history in S3
    history_obj = s3.get_object(Bucket=S3_BUCKET, Key=f"history/{batch.device_id}.json")
    history = json.loads(history_obj["Body"].read())
    history.append({"date": batch.date, "energy_kwh": summary["energy_kwh"]})
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=f"history/{batch.device_id}.json",
        Body=json.dumps(history),
    )

    if summary["energy_kwh"] == expected["expected_kwh"]:
        status = "matched"
    else:
        status = "mismatch"

    try:
        notify_operator(batch.device_id, status)
    except:
        pass

    return {"status": status, **summary, "api_key": API_KEY}


def notify_operator(device_id, status):
    requests.post(
        "http://notifier.internal/send",
        json={"device": device_id, "status": status},
    )
