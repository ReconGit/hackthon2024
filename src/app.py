from contextlib import asynccontextmanager

import uvicorn
from chatbot import Chatbot
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class Message(BaseModel):
    message: str


chatbot = Chatbot()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing app...")
    yield  # app is running asynchronously here
    print("Shutting down app...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "App is running!"}


@app.post("/chat")
async def send_message(message: Message):
    try:
        return {"completion": chatbot.get_completion(message.message)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


if __name__ == "__main__":
    # start the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # or in terminal: uvicorn main:app --reload
