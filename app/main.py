from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from config import settings
from db.database import wait_for_db,get_session,init_db
from fc_logger import get_logger
from models.users import User

logger = get_logger("fitcharge.main")

app = FastAPI()


@app.on_event("startup")
def on_startup():
    wait_for_db()
    init_db()


@app.post("/users/", response_model=User)
def create_user(user:User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
