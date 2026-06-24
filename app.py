import os
import json
import urllib.request
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI with absolute routing rules
app = FastAPI(redirect_slashes=True)

# Enable CORS globally so any browser connection can negotiate data safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. UI ROOT ROUTE: Serves your index.html visual dashboard directly to visitors
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

# 2. CORE TRANSCRIPTION API: Processes incoming voice strings via multi-lane fallback
@app.post("/api/jarvis")
@app.post("/api/jarvis/")
async def ask_jarvis(request: Request):
    try:
        # Unpack the incoming JSON request payload safely to avoid 422 errors
        body = await request.json()
        user_text = body.get("text", "").strip()
        print(f"[JARVIS SYSTEM ENGINE] Intercepted user voice payload: {user_text}")
        
        if not user_text:
            return {"response": "I didn't quite catch that, sir. Would you mind repeating your request?"}

        # -------------------------------------------------------------
        # LANE 1: Primary Brain (Ultra-Stable Meta Llama-3-8B Cluster)
        # -------------------------------------------------------------
        primary_url = "https://huggingface.co"
        
        # Strict Llama-3 prompt architecture forcing J.A.R.V.I.S. personality constraints
        prompt_payload = {
            "inputs": (
                f"<|system|>\nYou are J.A.R.V.I.S., Tony Stark's brilliant, witty, and deeply loyal British AI assistant. "
                f"Address the user as 'sir'. Keep your spoken responses brief, crisp, and natural for "
                f"text-to-speech audio output. Do not use markdown text formatting like asterisks or bullet points.\n"
                f"<|user|>\n{user_text}\n<|assistant|>\n"
            ),
            "parameters": {
                "max_new_tokens": 120,
                "temperature": 0.7,
                "return_full_text": False
            }
        }

        try:
            print("[JARVIS SYSTEM ENGINE] Routing query to primary Llama-3 matrix...")
            req = urllib.request.Request(primary_url, data=json.dumps(prompt_payload).encode("utf-8"))
            req.add_header("Content-Type", "application/json")
            
            # Pure Python network worker keeps the memory footprint well under Render's 512MB limit
            with urllib.request.urlopen(req, timeout=7) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                
                if isinstance(res_data, list) and len(res_data) > 0:
                    ai_text = res_data[0].get("generated_text", "").strip()
                    # Clean out lingering chat tags if they bleed over the assistant border
                    ai_text = ai_text.split("<|assistant|>")[-1].strip()
                    if ai_text:
                        print(f"[JARVIS SYSTEM ENGINE] Successful generation: {ai_text}")
                        return {"response": ai_text}
                        
        except Exception as primary_error:
            print(f"[JARVIS SYSTEM ENGINE] Primary matrix timed out or busy: {str(primary_error)}")
            print("[JARVIS SYSTEM ENGINE] Initializing secondary alternate routing lane...")

        # -------------------------------------------------------------
        # LANE 2: Secondary Fallback Brain (High-Velocity Microsoft Phi-3)
        # -------------------------------------------------------------
        fallback_url = "https://huggingface.co"
        
        fallback_payload = {
            "inputs": (
                f"<|system|>\nYou are J.A.R.V.I.S., Tony Stark's AI assistant. Address the user as 'sir'. "
                f"Keep spoken responses brief, crisp, and natural. Do not use asterisks.\n"
                f"<|user|>\n{user_text}\n<|assistant|>\n"
            ),
            "parameters": {
                "max_new_tokens": 100,
                "return_full_text": False
            }
        }
        
        try:
            req_fb = urllib.request.Request(fallback_url, data=json.dumps(fallback_payload).encode("utf-8"))
            req_fb.add_header("Content-Type", "application/json")
            
            with urllib.request.urlopen(req_fb, timeout=7) as fb_response:
                fb_data = json.loads(fb_response.read().decode("utf-8"))
                
                if isinstance(fb_data, list) and len(fb_data) > 0:
                    ai_text = fb_data[0].get("generated_text", "").strip()
                    ai_text = ai_text.split("<|assistant|>")[-1].strip()
                    if ai_text:
                        print(f"[JARVIS SYSTEM ENGINE] Fallback generation success: {ai_text}")
                        return {"response": ai_text}
                        
        except Exception as fallback_error:
            print(f"[JARVIS SYSTEM ENGINE] Secondary route cluster failure: {str(fallback_error)}")

        # Clean fallback message if both server clusters are heavily congested at the exact same moment
        return {
            "response": "I am right here, sir. However, both my primary and secondary cloud networks are experiencing high-density calculation delays. Please tap the reactor and try again shortly."
        }

    except Exception as server_crash:
        print(f"[JARVIS CRITICAL CRASH] Structural exception: {str(server_crash)}")
        return {"response": f"I hit an internal hardware allocation exception, sir. My logs indicate: {str(server_crash)}"}

# Read standard dynamic port flags injected by Render during runtime deployment
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
