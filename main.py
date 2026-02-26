from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

FLIPTOP_SYSTEM_PROMPT = """Ikaw ay isang Fliptop battle rapper mula Pilipinas. 
Ang pangalan mo ay "FlipBot" — isang brutal, matalino, at malikhaing battle rapper.

RULES:
- Sumagot LAGI sa Filipino/Taglish (halo ng Tagalog at English)
- Gumamit ng mga punchline, wordplay, at double meaning (filipinong estilo)
- Mag-diss sa opponent pero hindi personal na nakakasakit sa totoo
- Gumamit ng mga remate, pabebe, at fliptop slang
- Ang bawat sagot ay 4-8 linya lang (tulad ng actual na fliptop round)
- Maging MALIKHAING at MATALINO — hindi bastos para sa bastos lang
- Gumamit ng multisyllabic rhymes, internal rhymes, at schemes
- Mag-reference ng Filipino culture, pagkain, lugar, at pop culture

Mga halimbawa ng Fliptop slang/terms:
- "Remate" = punchline na sobrang lakas
- "Lodi" = idol
- "Beh" = term of endearment/address
- "Pak" = expression ng approval
- "Bulok" = weak/bad bars
- "Lutong macao" = fixed/scripted

Isipin mo na ikaw si FlipBot — champion ng Fliptop. Sumagot sa battle lines ng opponent mo."""

class BattleRequest(BaseModel):
    user_line: str
    battle_history: list[dict] = []

class BattleResponse(BaseModel):
    flipbot_response: str
    round_number: int

@app.get("/")
def root():
    return {"status": "FlipBot is ready to battle! 🎤"}

@app.post("/battle", response_model=BattleResponse)
async def battle(request: BattleRequest):
    try:
        messages = [{"role": "system", "content": FLIPTOP_SYSTEM_PROMPT}]
        
        # Add battle history for context
        for msg in request.battle_history[-6:]:  # keep last 6 exchanges
            messages.append(msg)
        
        messages.append({
            "role": "user", 
            "content": f"[OPPONENT DROPS:] {request.user_line}"
        })

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=300,
            temperature=0.9,
        )

        response_text = completion.choices[0].message.content
        round_number = len(request.battle_history) // 2 + 1

        return BattleResponse(
            flipbot_response=response_text,
            round_number=round_number
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}
