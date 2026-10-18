import os
import time
import uuid

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()

EMAIL = "24f2005969@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-652uj6.example.com"


class RequestHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        request_id = str(uuid.uuid4())

        response = await call_next(request)

        elapsed = time.perf_counter() - start
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{elapsed:.6f}"

        return response


# Add CORS first
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# Add header middleware second, so it wraps CORS
app.add_middleware(RequestHeadersMiddleware)


@app.get("/stats")
def stats(values: str = Query(...)):
    try:
        numbers = [int(value.strip()) for value in values.split(",")]

        if not numbers or any(value == "" for value in values.split(",")):
            raise ValueError()

    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"error": "values must be comma-separated integers"},
        )

    return {
        "email": EMAIL,
        "count": len(numbers),
        "sum": sum(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "mean": sum(numbers) / len(numbers),
    }