import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

# Initialize FastAPI
app = FastAPI(redirect_slashes=True)

# Enable CORS globally so any client or direct connection can stream data safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up explicit environment variable tracking fallback initialization
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("[CRITICAL WARNING]: GEMINI_API_KEY environment variable is completely missing on Render!")
    client = None
else:
    client = genai.Client(api_key=api_key)

# 1. ROOT ROUTE: Serves your index.html user interface directly to visitors
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    try:
        with open("index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>J.A.R.V.I.S Error: index.html missing from server root directory.</h1>", 
            status_code=404
        )

# 2. API ROUTE: Direct request parser to eliminate 422 errors entirely
@app.post("/api/jarvis")
@app.post("/api/jarvis/")
async def ask_jarvis(request: Request):
    try:
        # Manually unpack the payload data object to safely capture information strings
        body = await request.json()
        user_text = body.get("text", "")
        print(f"[JARVIS CORE] Processing voice string: {user_text}")
        
        if client is None:
            return {"response": "I apologize, sir. My global cloud cluster cannot find your Google API authentication key."}
            
        config = types.GenerateContentConfig(
            system_instruction=(
                "You are J.A.R.V.I.S., Tony Stark's brilliant, witty, and deeply loyal British AI assistant. "
                "Address the user as 'sir'. Keep your spoken responses brief, crisp, and natural for "
                "text-to-speech audio output. Do not use markdown text formatting like asterisks."
            ),
            max_output_tokens=150
        )
        
        # Switched to the highly stable 1.5 model lane to avoid 503 high-demand errors
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=user_text,
            config=config
        )
        
        if response and response.text:
            return {"response": response.text}
        else:
            return {"response": "I heard you clearly, sir, but my generative matrix returned an empty content package."}

    except Exception as e:
        print(f"[JARVIS CORE] Internal API Pipeline Crash: {str(e)}")
        return {"response": f"I hit an internal processing exception, sir. The system says: {str(e)}"}

# Dynamic production port configuration for Render's cloud infrastructure
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
