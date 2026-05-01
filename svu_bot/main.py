from fastapi import FastAPI, Body, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from svu_bot.bot import SVUBot
from contextlib import asynccontextmanager
from typing import Optional
import os
import shutil

# Global bot instance
bot = SVUBot()

# Ensure data directory exists
DATA_DIR = "svu_bot/data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="svu_bot/static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("svu_bot/static/index.html")

@app.post("/chat")
async def chat_endpoint(
    message: Optional[str] = Form(None),
    session_id: Optional[str] = Form("web_session"),
    file: Optional[UploadFile] = File(None)
):
    """API endpoint to chat with SVU Bot, supporting file attachments."""
    
    if not message and not file:
        return {"reply": "Please provide a message or a file."}

    if file:
        file_path = os.path.join(DATA_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        if not message or message.strip() == "":
            message = f"I've uploaded {file.filename}. Please analyze it."
        else:
            message = f"{message} (Context: I've also uploaded {file.filename})"

    # Fallback for message if somehow still None
    if not message:
        message = "Hello"

    response = await bot.chat(message, session_id=session_id or "web_session")
    return {"reply": response}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
