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
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app,
    like connecting to databases or initializing caches.

    :return: A future, so we need to wait for it
    :doc-author: Trelent
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    await FastAPILimiter.init(r)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# banned_ips = [ip_address("192.168.1.1"), ip_address("192.168.1.2")]


# @app.middleware("http")
# async def ban_ips(request: Request, call_next: Callable):
#     """
#     The ban_ips function is a middleware function that checks if the client's IP address is in the banned_ips list.
#     If it is, then we return a JSON response with status code 403 and an error message. If not, then we call the next
#     middleware function (or route handler) and return its response.
#
#     :param request: Request: Access the request object
#     :param call_next: Callable: Pass the next function in the middleware chain
#     :return: A response object, which is a json response with status code 403 and the content {
#     &quot;detail&quot;: &quot;you are banned&quot;}
#     :doc-author: Trelent
#     """
#     ip = ip_address(request.client.host)
#     if ip in banned_ips:
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
#     response = await call_next(request)
#     return response


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    The add_process_time_header function adds a header to the response called &quot;My-Process-Time&quot;
    that contains the time it took for this function to run. This is useful for debugging purposes.

    :param request: Request: Pass the request object to the function
    :param call_next: Call the next middleware in the chain
    :return: A response object with a new header
    :doc-author: Trelent
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["My-Process-Time"] = str(process_time)
    return response


@app.get("/", name='Корінь проекту')
def read_root():
    """
    The read_root function returns a dictionary with the key &quot;message&quot; and value &quot;REST APP v0.2&quot;.
    This function is used to test if the REST API is running.
    :return: A dictionary with a key &quot;message&quot; and value &quot;rest app v
    :doc-author: Trelent
    """
    return {"message": "REST APP v1.2"}


@app.get("/hw11/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks if the database is configured correctly.
    It does this by executing a SQL query and checking if it returns any results. If it doesn't, then there's something wrong with the database configuration.

    :param db: Session: Pass the database session to the function
    :return: A dictionary with a message
    :doc-author: Trelent
    """
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





