import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import urllib.request
import json

app = FastAPI(redirect_slashes=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root path delivers your visual dashboard
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    try:
        with open("index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>J.A.R.V.I.S Error: index.html missing.</h1>", status_code=404)

@app.post("/api/jarvis")
@app.post("/api/jarvis/")
async def ask_jarvis(request: Request):
    try:
        body = await request.json()
        user_text = body.get("text", "")
        print(f"[JARVIS HF-CORE] Processing query: {user_text}")
        
        # Free public serverless endpoint for Meta's Llama 3 (Ultra-stable alternative)
        api_url = "https://huggingface.co"
        
        # Strict prompt formatting to force the model to behave like J.A.R.V.I.S.
        prompt_payload = {
            "inputs": (
                f"<|system|>\nYou are J.A.R.V.I.S., Tony Stark's brilliant, witty, and deeply loyal British AI assistant. "
                f"Address the user as 'sir'. Keep your spoken responses brief, crisp, and natural for text-to-speech audio. "
                f"Do not use markdown text formatting like asterisks.\n<|user|>\n{user_text}\n<|assistant|>\n"
            ),
            "parameters": {
                "max_new_tokens": 120,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        req = urllib.request.Request(api_url, data=json.dumps(prompt_payload).encode("utf-8"))
        req.add_header("Content-Type", "application/json")
        
        # Execute pure Python web requests (Removes SDK version dependency issues)
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            
            # Hugging Face returns text variations inside list packages
            if isinstance(res_data, list) and len(res_data) > 0:
                ai_text = res_data[0].get("generated_text", "").strip()
                # Clean up any leftover instruction strings if they bleed through
                ai_text = ai_text.split("<|assistant|>")[-1].strip()
                return {"response": ai_text}
            
            return {"response": "I heard you, sir, but my local cognitive matrix failed to return a readable data array."}

    except Exception as e:
        print(f"[JARVIS HF-CORE] Crash: {str(e)}")
        return {"response": "I apologize, sir. I encountered a slight routing delay across the Hugging Face cluster."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
