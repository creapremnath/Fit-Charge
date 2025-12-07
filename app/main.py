"""
Private License (fitcharge)

This script is privately licensed and confidential. It is not intended for
public distribution or use without explicit permission from the owner.

All rights reserved (c) 2025.
"""

__author__ = "Premnath Palanichamy, Karthikeyan Kabilan"
__collaborators__ = "Premnath Palanichamy <creativepremnath@gmail.com>, Karthikeyan Kabilan <karthik.codes.dev@gmail.com>"
__copyright__ = "Copyright 2025, fitcharge"
__license__ = "Refer Terms and Conditions"
__version__ = "1.0"
__maintainer__ = "Premnath Palanichamy"
__status__ = "Development"
__desc__ = "Fitcharge main file"


from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm.collections import prepare_instrumentation
from app.core.database import wait_for_db,init_db
from app.core.fc_logger import get_logger
from app.api.v1.authentication.routes import router as auth_router
from app.api.v1.food.routes import router as food_router
from app.api.v1.user.routes import router as user_router
from app.api.v1.workout.routes import router as workout_router




logger = get_logger("fitcharge.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    wait_for_db()
    init_db()
    yield
    # Shutdown (if needed in the future)
    pass


app = FastAPI(
    title="Fit Charge",
    description="For Workouts tracking and calories tracking and gym volume tracking",
    version="1.0.0",
    swagger_ui_parameters={"syntaxHighlight": True},
    lifespan=lifespan
)

origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def health():
    return {"Health":"Server is Running"}


app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(food_router, prefix="/api/v1")
app.include_router(workout_router, prefix="/api/v1")

