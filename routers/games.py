from fastapi import APIRouter, Path, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from pydantic import BaseModel, Field

from starlette import status

from database import SessionLocal
from models import Games
from routers.auth import get_current_user

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
user_dependency = Annotated[dict, Depends(get_current_user)]

class GameRequest(BaseModel):
    title: str = Field(min_length=2)
    description: str = Field(max_length=200)
    rating: int = Field(gt=0, lt=6)

@router.get('/', status_code=status.HTTP_200_OK)
def get_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Not authenticated')

    game_model = db.query(Games).filter(Games.owner_id == user.get('id'))
    return game_model

@router.post('/add', status_code=status.HTTP_201_CREATED)
def add_game(user: user_dependency, db: db_dependency, game_request: GameRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Not authenticated')

    game_model = Games(**game_request.model_dump(), owner_id = user.get('id'))
    db.add(game_model)
    db.commit()

@router.put('/edit/{game_id}', status_code=status.HTTP_204_NO_CONTENT)
def edit_game(user: user_dependency, db: db_dependency, game_request: GameRequest, game_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Not authenticated')

    game_model = db.query(Games).filter(Games.id == game_id).first()
    if game_model is None:
        raise HTTPException(status_code=404, detail='Game not found')

    game_model.title = game_request.title
    game_model.description = game_request.description
    game_model.rating = game_request.rating

    db.add(game_model)
    db.commit()

@router.delete('/delete/{game_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_game(user: user_dependency, db: db_dependency, game_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Not authenticated')

    game_model = db.query(Games).filter(Games.id == game_id).first()
    if game_model is None:
        raise HTTPException(status_code=404, detail='Game not found')

    db.delete(game_model)
    db.commit()