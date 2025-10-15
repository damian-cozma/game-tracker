from fastapi import FastAPI
from routers import games

app = FastAPI()

@app.get('/')
def homepage():
    return 'Hello!'

app.include_router(games.router)