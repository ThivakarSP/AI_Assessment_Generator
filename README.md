# AI Assessment Generator

AI-powered educational content generation platform using Generator and Reviewer agents.

![AI Assessment](https://img.shields.io/badge/AI-Powered-6366f1) ![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688) ![React](https://img.shields.io/badge/Frontend-React-61dafb)

## 🌟 Features

- **Generator Agent**: Creates grade-appropriate educational content with explanations and MCQs
- **Reviewer Agent**: Validates content for age-appropriateness, accuracy, and clarity
- **Automatic Refinement**: If content fails review, it's automatically refined based on feedback
- **Beautiful UI**: Premium dark theme with animations and agent flow visualization

## 🚀 Quick Start

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env   # Add your OpenAI API key
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser

## 📁 Project Structure

```
ai-assessment/
├── backend/
│   ├── app/
│   │   ├── agents/           # Generator & Reviewer agents
│   │   ├── services/         # Orchestrator & LLM service
│   │   ├── models/           # Database models & Pydantic schemas
│   │   ├── routers/          # API endpoints
│   │   └── prompts/          # Agent system prompts
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main application component
│   │   ├── App.css           # Component styles
│   │   └── services/api.js   # API client
│   └── package.json
└── README.md
```

## 🔧 Configuration

### Backend (.env)
```
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=sqlite:///./ai_assessment.db
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate` | POST | Generate content for grade + topic |
| `/api/sessions/{id}` | GET | Get session status |
| `/api/sessions/{id}/generations` | GET | Get generation history |
| `/api/health` | GET | Health check |

## 🎨 Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic, OpenAI
- **Frontend**: React 18, Vite
- **Database**: SQLite (dev) / PostgreSQL (prod)
