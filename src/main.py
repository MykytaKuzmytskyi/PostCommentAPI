import uvicorn
from fastapi import FastAPI

from src.user.routers import router as user_routers
from src.post.routers import router as post_routers

app = FastAPI()

app.include_router(user_routers)
app.include_router(post_routers)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
