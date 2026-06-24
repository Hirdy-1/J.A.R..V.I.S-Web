import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(redirect_slashes=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client()

class QueryRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    try:
        with open("index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>J.A.R.V.I.S Error: index.html missing.</h1>", status_code=404)

@app.post("/api/jarvis")
@app.post("/api/jarvis/")
async def ask_jarvis(request: QueryRequest):
    # Print the incoming voice command to Render's live dashboard logs
    print(f"[JARVIS CORE] Processing voice string input: {request.text}")
    try:
        config = types.GenerateContentConfig(
            system_instruction=(
                "You are J.A.R.V.I.S., Tony Stark's brilliant, witty, and deeply loyal British AI assistant. "
                "Address the user as 'sir'. Keep your spoken responses brief, crisp, and natural for "
                "text-to-speech audio output. Do not use markdown text formatting like asterisks."
            ),
            max_output_tokens=150
        )
        
        # Call the model via the standard SDK path
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=request.text,
            config=config
        )
        
        # SAFE EXTRACT: Verify if valid candidates exist before pulling text
        if response.candidates and len(response.candidates) > 0:
            ai_text = response.text
            print(f"[JARVIS CORE] Success response: {ai_text}")
            return {"response": ai_text}
        else:
            print("[JARVIS CORE] Error: No response candidates found or prompt filtered.")
            return {"response": "I apologize, sir. My core processors failed to generate a matching verbal response."}

    except Exception as e:
        print(f"[JARVIS CORE] Internal pipeline error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
