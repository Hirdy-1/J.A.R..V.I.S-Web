import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

# Initialize FastAPI
app = FastAPI(redirect_slashes=True)

# Enable CORS (keeps things safe across networks)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Gemini SDK engine
client = genai.Client()

class QueryRequest(BaseModel):
    text: str

# 1. NEW ROOT ROUTE: Serves your index.html page directly to the browser
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    try:
        with open("index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>J.A.R.V.I.S Error: index.html missing from server directory.</h1>", status_code=404)

# 2. API ROUTE: Receives text from the frontend voice recognition
@app.post("/api/jarvis")
@app.post("/api/jarvis/")
async def ask_jarvis(request: QueryRequest):
    try:
        config = types.GenerateContentConfig(
            system_instruction=(
                "You are J.A.R.V.I.S., Tony Stark's brilliant, witty, and deeply loyal British AI assistant. "
                "Address the user as 'sir'. Keep your spoken responses brief, crisp, and natural for "
                "text-to-speech audio output. Do not use markdown text formatting like asterisks."
            ),
            max_output_tokens=150
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=request.text,
            config=config
        )
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Dynamic port assignment for Render cloud environment
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
