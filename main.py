import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware


from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from src.database.db import Base, engine
from src.routes import contacts, auth, users

app = FastAPI()

# setup CORS
origins = [
    "http://localhost",
    "http://localhost:8092",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create tables
Base.metadata.create_all(bind=engine)

# include routes
app.include_router(auth.router)
app.include_router(contacts.router)
app.include_router(users.router)

# setup rate limiting
@app.on_event("startup")
async def startup():
    r = await redis.Redis(host='localhost', port=6379, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)

# apply rate limiting to contacts routes
app.include_router(
    contacts.router,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))]
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8092)
