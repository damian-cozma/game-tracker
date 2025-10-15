from fastapi import APIRouter, Path
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import BaseModel, Field

from starlette import status

from database import SessionLocal
from models import Games

router = APIRouter(
    prefix='/games',
    tags=['games']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]

class GameRequest(BaseModel):
    title: str = Field(min_length=2)
    description: str = Field(max_length=200)
    rating: int = Field(gt=0, lt=6)

@router.get('/list', status_code=status.HTTP_200_OK)
def read_all(db: db_dependency):
    return db.query(Games).all()

@router.post('/add', status_code=status.HTTP_201_CREATED)
def add_game(db: db_dependency, game_request: GameRequest):
    game_model = Games(**game_request.model_dump())
    db.add(game_model)
    db.commit()

@router.put('/edit/{game_id}', status_code=status.HTTP_204_NO_CONTENT)
def edit_game(db: db_dependency, game_request: GameRequest, game_id: int = Path(gt=0)):
    game_model = db.query(Games).filter(Games.id == game_id).first()

    game_model.title = game_request.title
    game_model.description = game_request.description
    game_model.rating = game_request.rating

    db.add(game_model)
    db.commit()
