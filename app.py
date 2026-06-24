import os
import json
import urllib.request
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(redirect_slashes=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fetch your newly injected Hugging Face priority token
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    print("[JARVIS WARNING] HF_TOKEN environment variable is missing. Running on the slow public lane!")

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
        user_text = body.get("text", "").strip()
        print(f"[JARVIS HARDWARE ENGINE] User Request: {user_text}")
        
        if not user_text:
            return {"response": "I didn't quite catch that, sir."}
            
        # Target endpoint for Meta Llama-3 (Highly robust with authorization token)
        api_url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
        
        prompt_payload = {
            "inputs": (
                f"<|system|>\nYou are J.A.R.V.I.S., Tony Stark's brilliant, witty, and deeply loyal British AI assistant. "
                f"Address the user as 'sir'. Keep your spoken responses brief, crisp, and natural for "
                f"text-to-speech audio output. Do not use markdown text formatting like asterisks.\n"
                f"<|user|>\n{user_text}\n<|assistant|>\n"
            ),
            "parameters": {
                "max_new_tokens": 120,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        req = urllib.request.Request(api_url, data=json.dumps(prompt_payload).encode("utf-8"))
        req.add_header("Content-Type", "application/json")
        
        # If your token exists, attach it to your network headers for priority lane access
        if hf_token:
            req.add_header("Authorization", f"Bearer {hf_token}")
            
        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                
                if isinstance(res_data, list) and len(res_data) > 0:
                    ai_text = res_data[0].get("generated_text", "").strip()
                    ai_text = ai_text.split("<|assistant|>")[-1].strip()
                    if ai_text:
                        return {"response": ai_text}
        except Exception as e:
            print(f"[JARVIS PATHWAY ERROR] Primary Llama-3 lane exception: {str(e)}")

        # ----------------------------------------------------------------------
        # AUTOMATIC FAILOVER LANE: Routes instantly to an alternate model queue
        # ----------------------------------------------------------------------
        fallback_url = "https://huggingface.co"
        fb_payload = {
            "inputs": f"<|system|>\nYou are J.A.R.V.I.S., Tony Stark's assistant. Address the user as 'sir'. Keep spoken responses brief, crisp, and natural. No asterisks.\n<|user|>\n{user_text}\n<|assistant|>\n",
            "parameters": {"max_new_tokens": 100, "return_full_text": False}
        }
        
        req_fb = urllib.request.Request(fallback_url, data=json.dumps(fb_payload).encode("utf-8"))
        req_fb.add_header("Content-Type", "application/json")
        if hf_token:
            req_fb.add_header("Authorization", f"Bearer {hf_token}")
            
        with urllib.request.urlopen(req_fb, timeout=8) as fb_response:
            fb_data = json.loads(fb_response.read().decode("utf-8"))
            if isinstance(fb_data, list) and len(fb_data) > 0:
                ai_text = fb_data[0].get("generated_text", "").strip()
                return {"response": ai_text.split("<|assistant|>")[-1].strip()}

        return {"response": "I am online, sir, but both core cloud segments are failing to process queries."}

    except Exception as general_crash:
        print(f"[JARVIS CRITICAL FAULT] System Error: {str(general_crash)}")
        return {"response": f"Apologies sir, I hit a localized processing error: {str(general_crash)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
