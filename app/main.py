from fastapi import FastAPI

app = FastAPI(
    title='FastAPI Prosept Dealer'
)


@app.get('/')
async def main():
    return 'Hello World'
