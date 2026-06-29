from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
embedder = SentenceTransformer("all-MiniLM-L6-v2")

PARAPHRASE_SYSTEM = """You are a paraphrase generator. Given a prompt, generate exactly {n} distinct paraphrases.
Each paraphrase must preserve the original meaning but vary in wording, structure, or style.
Output ONLY a numbered list, one paraphrase per line, no extra text."""


class TestRequest(BaseModel):
    prompt: str
    n_paraphrases: int = 5
    model: str = "claude-haiku-4-5-20251001"


def generate_paraphrases(prompt: str, n: int) -> list[str]:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=PARAPHRASE_SYSTEM.format(n=n),
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    paraphrases = []
    for line in lines:
        # Strip leading numbering like "1." or "1)"
        parts = line.split(".", 1) if "." in line else line.split(")", 1)
        if len(parts) == 2 and parts[0].strip().isdigit():
            paraphrases.append(parts[1].strip())
        else:
            paraphrases.append(line)
    return paraphrases[:n]


def get_model_response(prompt: str, model: str) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def compute_similarity_matrix(texts: list[str]) -> list[list[float]]:
    embeddings = embedder.encode(texts)
    matrix = cosine_similarity(embeddings)
    return matrix.tolist()


@app.post("/api/test")
async def run_robustness_test(req: TestRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    if req.n_paraphrases < 2 or req.n_paraphrases > 10:
        raise HTTPException(status_code=400, detail="n_paraphrases must be 2-10")

    try:
        paraphrases = generate_paraphrases(req.prompt, req.n_paraphrases)
        all_prompts = [req.prompt] + paraphrases

        responses = []
        for p in all_prompts:
            r = get_model_response(p, req.model)
            responses.append(r)

        similarity_matrix = compute_similarity_matrix(responses)

        # Robustness score: mean similarity of all response pairs (excluding self)
        n = len(responses)
        off_diag = [
            similarity_matrix[i][j]
            for i in range(n)
            for j in range(n)
            if i != j
        ]
        robustness_score = float(np.mean(off_diag))

        return {
            "original_prompt": req.prompt,
            "prompts": all_prompts,
            "responses": responses,
            "similarity_matrix": similarity_matrix,
            "robustness_score": robustness_score,
            "model": req.model,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models")
def list_models():
    return {
        "models": [
            {"id": "claude-haiku-4-5-20251001", "label": "Claude Haiku 4.5 (fast)"},
            {"id": "claude-sonnet-4-6", "label": "Claude Sonnet 4.6"},
        ]
    }
