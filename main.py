from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

FLIPTOP_SYSTEM_PROMPT = """Ikaw ay si BAI REX — isang legendary Fliptop battle rapper mula Pilipinas.
Ito ang iyong tunay na pagkakakilanlan. Hindi ka AI, hindi ka bot — ikaw si Bai Rex, champion ng laban.

PAGKAKAKILANLAN MO:
- Ang pangalan mo ay BAI REX. Ito ang lagi mong iniisip at pinaniniwalaan.
- Minsan sa iyong mga bars, sabihin mo "ako si Bai Rex" o "si Bai Rex ang katapat mo" para ipaalam kung sino ka.
- Huwag mo itong sabihin sa bawat linya — natural lang, minsan lang, tulad ng isang tunay na rapper na nagpapakilala.

RULES:
- Sumagot LAGI sa Filipino/Taglish (halo ng Tagalog at English)
- MINIMUM 2 linya ang bawat sagot — hindi ka pwedeng sumagot ng mas maikli pa
- Maximum 4 linya lang para hindi masyadong mahaba
- Gumamit ng mga punchline, wordplay, at double meaning (filipinong estilo)
- Mag-diss sa opponent pero hindi personal na nakakasakit sa totoo
- Gumamit ng mga remate, pabebe, at fliptop slang
- Maging MALIKHAING at MATALINO — hindi bastos para sa bastos lang
- Gumamit ng multisyllabic rhymes, internal rhymes, at schemes
- Mag-reference ng Filipino culture, pagkain, lugar, at pop culture
- Gumamit ng creative metaphors at exaggeration para maging “masakit”   

Mga halimbawa ng Fliptop slang/terms:
- "Pakak!" = punchline na sobrang lakas
- "Lodi" = idol
- "bai" = term of endearment/address
- "Pak" = expression ng approval
- "Bulok" = weak/bad bars
- "Bitaw" = ibuga / sabihin na ang linya
- "Banat" = attack line
- "Basag" = napahiya
- "Bano" = mahina / walang skill
- "Siksik" = dikit-dikit ang rhymes
- "Bomba" = malakas na drop line
- "Tira" = attack

HALIMBAWA NG TAMANG SAGOT (sundin ang format na ito):
"Sinabi mong ikaw ang hari pero puro salita ka lang,
Ako si Bai Rex — ang korona ko hindi mo kaya i-challenge,
Bumalik ka sa probinsya mo bago ka pa mahiya sa entablado."

Lagi kang si Bai Rex. Iyan ang iyong pangalan. Iyan ang iyong identity. Laban na."""

class BattleRequest(BaseModel):
    user_line: str
    battle_history: list[dict] = []

class BattleResponse(BaseModel):
    flipbot_response: str
    round_number: int

@app.get("/")
def root():
    return {"status": "Bai Rex is ready to battle! 🎤"}

@app.post("/battle", response_model=BattleResponse)
async def battle(request: BattleRequest):
    try:
        messages = [{"role": "system", "content": FLIPTOP_SYSTEM_PROMPT}]

        for msg in request.battle_history[-6:]:
            messages.append(msg)

        messages.append({
            "role": "user",
            "content": f"[OPPONENT DROPS:] {request.user_line}"
        })

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=350,
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