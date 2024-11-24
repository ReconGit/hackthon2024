from contextlib import asynccontextmanager
from textwrap import dedent
from typing import Optional

import pymupdf as fitz
import uvicorn
from fastapi import FastAPI, Form, HTTPException, UploadFile

from chatbot import Chatbot

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
    try:
        if session_id not in session_history:
            session_history[session_id] = []
        message_history: list[dict] = session_history[session_id]
        message_history.append({"role": "user", "content": message})

        completion = chatbot.get_chat_completion(message_history)
        message_history.append({"role": "assistant", "content": completion})

        return {"completion": completion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.post("/structure")
async def structure(
    session_id: str = Form(...),
    message: str = Form(...),
    files: Optional[list[UploadFile]] = None,
):
    try:
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

            structure_message = message + "\nUploaded documents:\n".join(file_contents)
        else:
            structure_message = message
        message_history.append({"role": "user", "content": structure_message})

        structure = chatbot.get_structured_output(message_history)

        return {"structure": structure}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.post("/improvements")
async def structure(
    session_id: str = Form(...),
    message: str = Form(...),
    files: Optional[list[UploadFile]] = None,
):
    try:
        if session_id not in session_history:
            session_history[session_id] = []
        message_history: list[dict] = session_history[session_id]

        if files:
            file_content1 = []
            file1 = files[0]
            content = await file1.read()
            pdf_document = fitz.open(stream=content, filetype="pdf")
            extracted_text = ""
            for page in pdf_document:
                extracted_text += page.get_text()
            file_content1.append(extracted_text)

            file_content2 = []
            file2 = files[1]
            content = await file2.read()
            pdf_document = fitz.open(stream=content, filetype="pdf")
            extracted_text = ""
            for page in pdf_document:
                extracted_text += page.get_text()
            file_content2.append(extracted_text)

            prompt = dedent(
                f"""
                This is my filled form: 
                {file_content1}

                This is the template form:
                {file_content2}

                Please suggest improvements to my filled form.
                """
            ).strip()
            improvement_message = message + prompt
        else:
            improvement_message = message
        message_history.append({"role": "user", "content": improvement_message})

        structure = chatbot.get_structured_output(message_history)

        return {"improvements": structure}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


if __name__ == "__main__":
    # start the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # or in terminal: uvicorn main:app --reload
