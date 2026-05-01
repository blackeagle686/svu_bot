import os
import subprocess
import time
import sys

def install_dependencies():
    print("Installing required Python packages (batched)...")

    # In Colab / ephemeral environments, apt-get (Redis) is slow. Skip by default.
    # To force install system packages (slow), set INSTALL_REDIS=1 in the environment.
    install_redis = os.environ.get("INSTALL_REDIS", "0") == "1"

    if install_redis:
        print("INSTALL_REDIS=1 -> installing redis-server via apt (this may take a while)...")
        subprocess.check_call(["apt-get", "update"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.check_call(["apt-get", "install", "-y", "redis-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            subprocess.check_call(["service", "redis-server", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            # best-effort start
            pass
    else:
        print("Skipping apt-get redis install. Set INSTALL_REDIS=1 to enable it.")

    # Batch pip install to reduce overhead; use --no-cache-dir and quiet output to speed up.
    pip_packages = [
        "pyngrok",
        "uvicorn",
        "fastapi",
        "python-multipart",
        "redis",
        "pypdf",
        "python-docx",
        "pandas",
        "openpyxl",
        "beautifulsoup4",
        "requests",
    ]
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "-q"] + pip_packages)

def setup_ngrok(auth_token):
    from pyngrok import ngrok
    print("Setting up ngrok tunnel...")
    ngrok.set_auth_token(auth_token)
    # Use a non-blocking connect and return the public URL
    tunnel = ngrok.connect(8000)
    public_url = tunnel.public_url
    print(f"\n{'='*50}")
    print(f"SVU Bot is now LIVE at: {public_url}")
    print(f"{'='*50}\n")
    return public_url

def run_server():
    print("Starting FastAPI server...")
    # Using subprocess to run the main bot script in the background or backgrounded thread
    # In Colab, we usually run this in a separate cell, but here we can use uvicorn directly
    import uvicorn
    from svu_bot.main import app
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    NGROK_TOKEN = "36jW6kAV8Inp5SHYiuIicuuRols_7NkiWdLme3iULLJx3gMS5"
    
    try:
        install_dependencies()
        public_url = setup_ngrok(NGROK_TOKEN)
        run_server()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
