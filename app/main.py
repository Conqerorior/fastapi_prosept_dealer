from fastapi import FastAPI

from app.auth.routers import user_router

app = FastAPI(title='FastAPI Prosept Dealer')

app.include_router(user_router)


@app.get('/')
async def main():
    return 'Hello World'
