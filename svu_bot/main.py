from fastapi import FastAPI, Body, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from svu_bot.bot import SVUBot
from contextlib import asynccontextmanager
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
    message: str = Form(...),
    session_id: str = Form("web_session"),
    file: UploadFile = File(None)
):
    """API endpoint to chat with SVU Bot, supporting file attachments."""
    
    if file:
        file_path = os.path.join(DATA_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # If a file was uploaded, we might want to slightly modify the prompt
        # to ensure the bot looks at the new data.
        if not message or message.strip() == "":
            message = f"I've uploaded {file.filename}. Please analyze it."
        else:
            message = f"{message} (Context: I've also uploaded {file.filename})"

    response = await bot.chat(message, session_id=session_id)
    return {"reply": response}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
