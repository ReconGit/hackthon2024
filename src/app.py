from contextlib import asynccontextmanager
from textwrap import dedent
from typing import Optional

import pymupdf as fitz
import uvicorn
from chatbot import Chatbot
from fastapi import FastAPI, Form, HTTPException, UploadFile

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


@app.post("/analysis")
async def analysis(
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
            file_names = []
            for file in files:
                file_name = file.filename
                file_names.append(file_name)
                content = await file.read()
                pdf_document = fitz.open(stream=content, filetype="pdf")
                extracted_text = ""
                for page in pdf_document:
                    extracted_text += page.get_text()
                file_contents.append(f'Extracted text from file "{file_name}":\n{extracted_text}\n\n')

            prompt_message = dedent(
                f"""
                The documents I upload are called {file_names[0]} and {file_names[1]}.
                {file_names[0]} is a template form and {file_names[1]} is the form filled by the user.

                This is the extracted text from the template document:
                {file_contents[0]}

                This is the extracted text from the filled document:
                {file_contents[1]}

                Please suggest improvements to the filled form based on the template form.
                """
            ).strip()

            print(prompt_message)
        else:
            prompt_message = message
        message_history.append({"role": "user", "content": prompt_message})

        analysis = chatbot.get_analysis(message_history)

        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


if __name__ == "__main__":
    # start the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # or in terminal: uvicorn main:app --reload
