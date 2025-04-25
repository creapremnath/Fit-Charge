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
from fastapi.middleware.cors import CORSMiddleware
from db.database import wait_for_db,init_db,create_database_if_not_exists
from fc_logger import get_logger

from routers import user,workout


logger = get_logger("fitcharge.main")

app = FastAPI(
    title="Fit Charge",
    description="A Fitness Application.",
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
    create_database_if_not_exists()
    wait_for_db()
    init_db()


app.include_router(user.router)
app.include_router(workout.router)