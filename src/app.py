from contextlib import asynccontextmanager
from typing import Optional

import fitz
import uvicorn
from chatbot import Chatbot
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel


class Message(BaseModel):
    session_id: str
    message: str


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
async def chat(
    session_id: str = Form(...),
    message: str = Form(...),
    files: Optional[list[UploadFile]] = None,
):
    print(f"Received message: {message}")
    print(f"Received files: {files}")
    try:
        if not message and not files:
            raise HTTPException(status_code=400, detail="No message or files provided")

        if session_id not in session_history:
            session_history[session_id] = []
        message_history: list[dict] = session_history[session_id]

        if files:
            file_contents = []
            for file in files:
                content = await file.read()
                pdf_document = fitz.open(stream=content, filetype="pdf")
                extracted_text = ""
                for page in pdf_document:
                    extracted_text += page.get_text()
                file_contents.append(extracted_text)
                print(f"Extracted text from {extracted_text}")

            files_message = message + "\nUploaded documents:\n".join(file_contents)
            message_history.append({"role": "user", "content": files_message})
        else:
            message_history.append({"role": "user", "content": message})

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
async def upload_pdf(files: list[UploadFile]):
    try:
        file_contents = []
        for file in files:
            content = await file.read()
            pdf_document = fitz.open(stream=content, filetype="pdf")
            extracted_text = ""
            for page in pdf_document:
                extracted_text += page.get_text()
            file_contents.append(extracted_text)

        return {"text": file_contents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


if __name__ == "__main__":
    # start the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # or in terminal: uvicorn main:app --reload
