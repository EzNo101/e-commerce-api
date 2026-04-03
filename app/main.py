from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.api import router

app = FastAPI(lifespan=lifespan)
app.include_router(router)
