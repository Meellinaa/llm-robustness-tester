# LLM Robustness Tester

> How consistent is an AI model when you ask the same question different ways?

## What It Does

You type a prompt. The app rewrites it 5 different ways (same meaning, different words), sends all versions to an AI model, and measures how much the answers differ from each other.

- **High score (green)** → the model is consistent and reliable
- **Low score (red)** → the model is brittle — small wording changes cause big answer changes

## Why It Matters

AI companies pay people to find these weaknesses. This is called **LLM evaluation** and **red-teaming** — one of the hottest skills in AI right now.

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python, FastAPI |
| AI / Paraphrasing | Anthropic Claude API |
| Similarity Scoring | sentence-transformers, scikit-learn, NumPy |
| Frontend | Vanilla JS, HTML/CSS |
| Report Export | Client-side HTML → printable PDF |

## Features

- Auto-generates N paraphrases of any prompt
- Runs all variants through Claude (Haiku or Sonnet)
- Computes a **robustness score** (0–100%)
- Renders a **color-coded similarity heatmap**
- **Downloadable report** with all prompts, responses, and scores

## How to Run

```bash
# 1. Add your API key
cp backend/.env.example backend/.env
# edit backend/.env → ANTHROPIC_API_KEY=your_key

# 2. Start the backend
./start.sh

# 3. Open frontend/index.html in your browser
```

## Project Structure

```
llm-robustness-tester/
├── backend/
│   ├── main.py          # FastAPI server
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── index.html       # Full UI, no build step
└── start.sh             # One-command setup
```

## Built By

Melina Fathidashtaki — github.com/Meellinaa
