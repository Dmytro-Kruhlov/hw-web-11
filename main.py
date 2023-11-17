import time
from ipaddress import ip_address
from typing import Callable

import redis.asyncio as redis

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.routes import contacts, auth, users
from src.conf.config import settings
app = FastAPI()


@app.on_event("startup")
async def startup():
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    await FastAPILimiter.init(r)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

banned_ips = [ip_address("192.168.1.1"), ip_address("192.168.1.2")]


@app.middleware("http")
async def ban_ips(request: Request, call_next: Callable):
    ip = ip_address(request.client.host)
    if ip in banned_ips:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
    response = await call_next(request)
    return response


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["My-Process-Time"] = str(process_time)
    return response


@app.get("/", name='Корінь проекту')
def read_root():
    return {"message": "REST APP v1.2"}


@app.get("/hw11/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:

        result = db.execute(text("SELECT 1")).fetchone()
        print(result)
        if result is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error connecting to the database")


app.include_router(contacts.router, prefix='/hw11')
app.include_router(auth.router, prefix='/hw11')
app.include_router(users.router, prefix='/hw11')





