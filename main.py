from fastapi import FastAPI
from routers import games, auth

app = FastAPI()

@app.get('/')
def homepage():
    return 'Hello!'

app.include_router(games.router)
app.include_router(auth.router)