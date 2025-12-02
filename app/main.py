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


from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm.collections import prepare_instrumentation
from core.database import wait_for_db,init_db
from core.fc_logger import get_logger
from api.v1.authentication.routes import router as auth_router
from api.v1.food.routes import router as food_router
from api.v1.user.routes import router as user_router
from api.v1.workout.routes import router as workout_router




logger = get_logger("fitcharge.main")

app = FastAPI(
    title="Fit Charge",
    description="For Workouts tracking and calories tracking and gym volume tracking",
    version="1.0.0",
    swagger_ui_parameters={"syntaxHighlight": True}
)

origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    wait_for_db()
    init_db()



app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(food_router, prefix="/api/v1")
app.include_router(workout_router, prefix="/api/v1")

