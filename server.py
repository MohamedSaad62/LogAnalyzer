from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
from db import push_to_db
app = FastAPI()

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GEMINI_API = "AIzaSyBXqpjAStyXL-RVkNbLEXMsH7gB53yajZY" # I left it hard coded so you can run the code if you want not a big secret anyway
# --- Main page endpoint ---
@app.get("/")
def main():
    return FileResponse("HTML/index.html")

# --- Request models ---
class LogRequest(BaseModel):
    log: str

class ChatRequest(BaseModel):
    message: str

# --- LLM A: log analyzer ---
@app.post("/llm_a")
async def llm_a(req: LogRequest):
    log_text = req.log
    prompt = (
    "I will give you logs. Your task is to extract only the error lines "
    "and after each error, output a suggestion to fix it. "
    "STRICT FORMAT (no extra words, no markdown, no introductions): "
    "error_message $#$ suggestion $#$\n"
    "DON'T output any newlines even in the end" 
    "Each suggestion <= 50 words\n"
    "Now here are the logs:\n"
    f"{log_text}"
    )	
    headers = {
    "Content-Type": "application/json",
    "X-goog-api-key": GEMINI_API
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    try:
        reply = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        reply =  str(result)
    #await push_to_db(log_text, reply) if this uncomment then it needs proper database setup 	  	
    reply = reply.replace("\n", "")	 
    reply = reply.split("$#$")
    n = len(reply)
    i = 0
    err = []
    rep = []
    while(i < n - 1):
        err.append(reply[i])
        rep.append(reply[i+1])
        i += 2	
    return {
        "errors": err,
        "suggestions": rep,
    }

# --- LLM B: free chat ---
@app.post("/llm_b")
async def llm_b(req: ChatRequest):
    user_msg = req.message
    user_msg += 'answer me with no more than 200 words' # this add because of very long response of gemini which might be not practical
    headers = {
    "Content-Type": "application/json",
    "X-goog-api-key": GEMINI_API
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": user_msg}
                ]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    try:
        reply = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        reply =  str(result)    
    return {"reply": reply}
