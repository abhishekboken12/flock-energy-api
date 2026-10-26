import httpx
from fastapi import FastAPI, HTTPException, Query
from dotenv import load_dotenv

from app.client import UrjaPortalClient

load_dotenv()

app = FastAPI(
    title="Flock Energy Meter API",
    description="REST API wrapper for the Urja Meter Ops portal",
    version="1.0.0",
)

portal = UrjaPortalClient()


@app.get("/api/v1/meters")
def list_meters(
    page: int = Query(default=1, ge=1),
    q: str = Query(default=""),
):
    try:
        return portal.get_meters(page=page, query=q)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="The legacy portal rejected the request.",
        )
    except (httpx.RequestError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/api/v1/meters/{meter_id}")
def read_meter(meter_id: str):
    try:
        return portal.get_meter_details(meter_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="The legacy portal rejected the request.",
        )
    except (httpx.RequestError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/api/v1/meters/{meter_id}/geo")
def read_meter_geo(meter_id: str):
    try:
        return portal.get_meter_geo(meter_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="The legacy portal rejected the request.",
        )
    except (httpx.RequestError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/api/v1/meters/{meter_id}/energy")
def read_meter_energy(meter_id: str):
    try:
        return portal.get_meter_energy(meter_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="The legacy portal rejected the request.",
        )
    except (httpx.RequestError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))
