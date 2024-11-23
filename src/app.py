from contextlib import asynccontextmanager
from typing import List

import fitz
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from chatbot import Chatbot


class Message(BaseModel):
    session_id: int


chatbot = Chatbot()
session_history = {}


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
async def chat(message: Message, files: List[UploadFile] = File(...)):
    try:
        if message.session_id not in session_history:
            session_history[message.session_id] = []
        message_history: list[dict] = session_history[message.session_id]

        if files:
            file_contents = []
            for file in files:
                content = await file.read()
                pdf_document = fitz.open(stream=content, filetype="pdf")
                extracted_text = ""
                for page in pdf_document:
                    extracted_text += page.get_text()
                file_contents.append(extracted_text)

            files_message = message.message + "\nUploaded documents:\n".join(file_contents)
            message_history.append({"role": "user", "content": files_message})
        else:
            message_history.append({"role": "user", "content": message.message})

        completion = chatbot.get_chat_completion(message_history)
        message_history.append({"role": "assistant", "content": completion})

        return {"completion": completion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.post("/structure")
async def structure(message: Message):
    try:
        structure = chatbot.get_structured_output(message.message)
        return {"structure": structure}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.post("/upload-pdf")  # DEPRECATED
async def upload_pdf(file: UploadFile = File(...)):
    try:
        content = await file.read()
        pdf_document = fitz.open(stream=content, filetype="pdf")
        extracted_text = ""
        for page in pdf_document:
            extracted_text += page.get_text()

        return {"text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


if __name__ == "__main__":
    # start the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # or in terminal: uvicorn main:app --reload
