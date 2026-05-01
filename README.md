# CyberHire AI - Cybersecurity Soft Skills Assessment

**Final Year Project (FYP)**  
A Hybrid LLM-Rule-Based AI system for Soft-skill Evaluation in Senior Cybersecurity Recruitement
---

## Quick Start

### Prerequisites
- **Python 3.10, 3.11, or 3.12** (NOT 3.13 - not supported)
  - Check: `python --version`
- **Node.js 18+** (check: `node --version`)
- **API Key Provided** - `.env` file with GROQ API key is included in `backend/` folder

### 1. Extract & Navigate
Unzip the submission, then in terminal:
```bash
cd FYP
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

**API key is already provided** in `backend/.env` - no setup needed.

If you need to use your own key, edit `backend/.env`:
```
GROQ_API_KEY=your_api_key_here
```

Run the backend:
```bash
python main.py
```

If `.env` doesn't load (rare case), set the API key manually:
```bash
# Windows PowerShell:
$env:GROQ_API_KEY="ur own api key"
python main.py

# Mac/Linux:
export GROQ_API_KEY="ur own api key"
python main.py
```
→ API starts at **http://localhost:8000**  
→ Documentation: http://localhost:8000/docs

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
→ App starts at **http://localhost:5173**

---

## How It Works

Evaluates 4 cybersecurity soft skills using 3 layers:

| Layer | Method | Weight |
|-------|--------|--------|
| 1 | Rule-based STAR Filter | 20% |
| 2 | LLM Quality Evaluation (Groq) | 75% |
| 3 | Expert Answer Comparison | 5% |

**Skills assessed:** Communication, Leadership, Decision Making, Critical Thinking

---

## Project Structure

```
FYP/
├── backend/              # FastAPI server
│   ├── main.py
│   ├── chatbot_engine.py
│   ├── llm_evaluator.py
│   ├── rule_based_filter.py
│   ├── hybrid_scorer.py
│   ├── expert_comparator.py
│   ├── database.py
│   └── requirements.txt
├── frontend/             # React + Vite
│   └── src/
├── data/                 # Questions & test data
│   ├── final 16.json
│   ├── expert_answers.json
│   └── MATCHED_TEST_RESPONSES_16.md
└── tests/                # All test scripts
    ├── test_chatbot.py
    ├── test_integration.py
    ├── test_three_layer.py
    ├── test_interview_against_ai.py
    ├── evaluate_system.py
    ├── multi_ai_validator.py
    ├── multi_model_groq_test.py
    └── weight_ablation_study.py
```

---

## Running Tests

```bash
cd tests

# Main evaluation test (16 questions, takes ~3 mins)
python test_interview_against_ai.py

# Integration test
python test_integration.py

# Unit tests
python test_chatbot.py
python test_three_layer.py
```

---

## Troubleshooting

**Backend won't start:**
- Check Python 3.10+: `python --version`
- Verify `.env` file exists with valid `GROQ_API_KEY`
- Ensure port 8000 is free

**Frontend won't start:**
- Check Node.js 18+: `node --version`
- Delete `node_modules` and run `npm install` again

**API can't find questions:**
- Verify `data/final 16.json` exists
- System uses fallback questions if file is missing

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/interview/start` | POST | Start interview |
| `/api/interview/respond` | POST | Submit response |
| `/api/interview/{id}/report` | GET | Get final report |
| `/docs` | GET | API documentation |

---

## Key Results

- **Accuracy:** 80% (±3 points of ground truth)
- **MAE:** 2.52
- **Model:** Groq Llama 3.3 70B

---

## Technologies

**Backend:** Python, FastAPI, SQLAlchemy, Groq API, SQLite  
**Frontend:** React, Vite, TailwindCSS, Recharts

---

## Academic Context

**Research Question:** How can AI evaluate soft skills in cybersecurity professionals?

**Theoretical Framework:**
- STAR Method (MIT Career Advising)
- NIST NICE Workforce Framework (SP 800-181)
- Behavioral Cybersecurity (Dawson & Thomson, 2018)

---

## License 
This project is developed for academic purposes.
