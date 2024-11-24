import zipfile
from contextlib import asynccontextmanager
from pathlib import Path
from textwrap import dedent
from typing import Optional

import pymupdf as fitz
import uvicorn
from chatbot import Chatbot
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, UploadFile
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_parse import LlamaParse

load_dotenv()


chatbot = Chatbot()
parser = LlamaParse(
    result_type="text",  # type: ignore
)  # "markdown" and "text" are available
file_extractor = {".pdf": parser}

session_history = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing app...")
    yield  # app is running asynchronously here
    print("Shutting down app...")
    # remove cache folder


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


@app.post("/summary")
async def summary(
    session_id: str = Form(...),
    message: str = Form(...),
    files: Optional[list[UploadFile]] = None,
):
    try:
        if session_id not in session_history:
            session_history[session_id] = []
        message_history: list[dict] = session_history[session_id]
        message_history.append({"role": "user", "content": message})

        summary = chatbot.get_summary(message_history)
        message_history.append({"role": "assistant", "content": summary})

        return {"summary": summary}
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
            idx = 0
            zipper = None
            for file in files:
                file_name = file.filename
                file_names.append(file_name)
                content = await file.read()
                idx += 1
                if idx > 2:
                    zipper = content
                    break
                pdf_document = fitz.open(stream=content, filetype="pdf")
                extracted_text = ""
                for page in pdf_document:
                    extracted_text += page.get_text()
                file_contents.append(f'Extracted text from file "{file_name}":\n{extracted_text}\n\n')

            if len(files) == 3:
                # save the historic data to a folder and unzip it
                save_path = Path("historic")
                save_path.mkdir(parents=True, exist_ok=True)
                # save the file
                # save the file with privelaged permissions
                zip_file_path = save_path / "data.zip"  # Create a full path with filename
                with open(zip_file_path, "wb") as f:
                    f.write(zipper)
                # unzip the file
                with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                    zip_ref.extractall(save_path)

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

        else:
            prompt_message = message

        message_history.append({"role": "user", "content": prompt_message})
        analysis = chatbot.get_analysis(message_history)

        return {"analysis": analysis}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}")


if __name__ == "__main__":
    # start the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # or in terminal: uvicorn main:app --reload
