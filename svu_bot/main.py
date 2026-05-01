from fastapi import FastAPI, Body, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from svu_bot.bot import SVUBot
from contextlib import asynccontextmanager
from typing import Optional
import os
import shutil

# File text extraction helper (best-effort)
from svu_bot.utils.file_extractor import extract_text

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

        # Best-effort: extract a truncated text excerpt so the bot can analyze immediately
        try:
            excerpt = extract_text(file_path, max_chars=4000)
        except Exception:
            excerpt = ""

        if not message or message.strip() == "":
            # No custom prompt – use generic analysis request
            message = f"I've uploaded '{file.filename}'. Please analyze it and provide a comprehensive summary."
        else:
            # User chose a smart prompt chip (e.g. "Summarize this file") – keep intent, add file context
            message = f"{message} The file I'm referring to is: '{file.filename}' (just uploaded)."

        # If we extracted an excerpt, include it in the prompt so the LLM can respond immediately.
        if excerpt:
            # Keep the message concise but useful; mark excerpt as truncated when applicable.
            message += f"\n\nFile excerpt:\n{excerpt}"

    # Fallback for message if somehow still None
    if not message:
        message = "Hello"

    response = await bot.chat(message, session_id=session_id or "web_session")
    return {"reply": response}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
