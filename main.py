from fastapi import FastAPI

import os

from auth import auth_router
from api import api_router

app = FastAPI()

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google_key.json"

app.include_router(auth_router, prefix="/auth")
app.include_router(api_router, prefix="/api")
