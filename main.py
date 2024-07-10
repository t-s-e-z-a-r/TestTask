from fastapi import FastAPI

import os

from auth import auth_router
from api import api_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(api_router, prefix="/api")
