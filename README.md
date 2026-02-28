# Anchor — Backend API

> FastAPI backend powering the Anchor mental wellness platform

This is the backend API for Anchor — an AI-powered mental
wellness platform built for AMD Slingshot 2025.

**Frontend Repository:** https://github.com/Khushicodes15/Anchor
**Live App:** https://anchor-topaz.vercel.app/

---

## Overview

The backend is a Python FastAPI application hosted on Render.
It handles journal storage and retrieval, AI pipeline
orchestration, safety plan management, crisis session
tracking, community story moderation, and therapist
connection features. Firebase Firestore is used as the
primary database and Firebase Authentication handles all
user identity and token verification.

---

## Core Responsibilities

**Journal API**
Stores and retrieves journal entries per user. Each entry
is processed through Azure AI Language for sentiment
analysis, opinion mining, and key phrase extraction before
being saved. Results are stored alongside the entry to
power the AI Early Warning System and Anchor Wrapped.

**AI Orchestration**
Coordinates calls between Google Gemini (narrative
reflection generation) and Azure AI Language (emotional
analysis). Manages prompt construction ensuring no
personally identifiable information is passed to external
AI services.

**Safety Plan API**
Full CRUD operations for personalized safety plans.
Each plan stores triggers, coping strategies, safe
contacts, and reasons to live. Safety plan data is
retrieved directly during Crisis Mode activation.

**Crisis Session API**
Handles crisis session start and end events. Logs
session metadata for pattern tracking without storing
sensitive crisis content. Retrieves the active safety
plan to serve during the crisis flow.

**Community API**
Receives story submissions and passes them through
Azure AI Content Safety before storing in Firestore.
Serves approved stories to the Community Library.
Handles like and save interactions.

**Early Warning System**
Runs periodic analysis across recent journal sentiment
scores. When emotional decline is detected across
multiple entries, triggers a Firebase Cloud Messaging
push notification to the user — gentle, non-alarming,
and non-diagnostic.



---

## Tech Stack

**Framework:** FastAPI (Python)
**Language:** Python 3.11+
**Database:** Firebase Firestore
**Authentication:** Firebase Admin SDK
**AI — Journaling:** Google Gemini API
**AI — Sentiment Analysis:** Azure AI Language
**AI — Content Moderation:** Azure AI Content Safety
**Push Notifications:** Firebase Cloud Messaging
**Deployment:** Render

---

## Project Structure
```
anchor-backend/
├── main.py
├── routers/
│   ├── __init__.py
│   └── auth.py
│   ├── dashboard.py
│   └── notifications.py
│   ├── journal.py
│   ├── safety.py
│   ├── crisis.py
│   ├── community.py
│   └── wrapped.py
├── models/
│   ├── __init__.py
│   └── schemas.py
├── services/
│   └──  __init__.py
│   ├── ai_pipeline.py
│   ├── azure_safety.py
│   ├── azure_language.py
│   └── auth.py
│   ├── firebase.py
│   ├── gemini.py
│   └── notifications.py
│   └── speech.py
├── utils/
│   └── prompt_builder.py
├── requirements.txt
└── .env
```

---

## API Endpoints

**Journals**
POST /journals — create new journal entry
GET /journals — retrieve user journal history
GET /journals/{id} — retrieve single entry
DELETE /journals/{id} — delete entry

**Safety Plan**
POST /safety-plan — create safety plan
GET /safety-plan — retrieve active plan
PUT /safety-plan — update plan
DELETE /safety-plan — delete plan

**Crisis**
POST /crisis/start — log crisis session start
GET /crisis/support — retrieve safety plan for crisis flow
POST /crisis/end — log crisis session end

**Community**
GET /community/fetch/stories — retrieve approved stories
POST /community/post/story — submit story for moderation

**Wrapped**
GET /wrapped — retrieve aggregated emotional summary

---

## Getting Started

### Prerequisites
- Python 3.11+
- pip
- Firebase project with Firestore enabled
- Firebase Admin SDK service account JSON
- Google Gemini API key
- Azure AI Language endpoint and key
- Azure AI Content Safety endpoint and key

### Installation
```bash
# Clone the repository
git clone https://github.com/Khushicodes15/anchor-backend.git
cd anchor-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

### Environment Variables

Create a `.env` file in the root directory.
All secrets are stored as environment variables —
no keys are present in the codebase.
```env
# Firebase Admin
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=your_client_email

# Google Gemini
GEMINI_API_KEY=your_gemini_key

# Azure AI Language
AZURE_LANGUAGE_KEY=your_key
AZURE_LANGUAGE_ENDPOINT=your_endpoint

# Azure AI Content Safety
AZURE_CONTENT_SAFETY_KEY=your_key
AZURE_CONTENT_SAFETY_ENDPOINT=your_endpoint

# App
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,https://anchor-topaz.vercel.app
```

### Run Locally
```bash
uvicorn main:app --reload
```

API will be available at http://localhost:8000
Interactive docs at http://localhost:8000/docs

---

## Deployment

The backend is deployed on Render as a web service.
Set all environment variables in Render under
Environment → Environment Variables before deploying.

The start command used on Render:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Authentication

Every protected endpoint verifies the Firebase ID token
sent in the Authorization header from the frontend.
The Firebase Admin SDK decodes and validates the token
server-side. No session cookies are used — all auth is
stateless and token-based.
```
Authorization: Bearer <firebase_id_token>
```

---

## Security Practices

- All API keys stored as environment variables only
- Firebase token verification on every protected route
- No personally identifiable data passed to external AI APIs
- HTTPS enforced on all Render deployments
- CORS restricted to known frontend origins only
- Firestore security rules enforce per-user data access

---

## Related

**Frontend:** https://github.com/Khushicodes15/Anchor
**Live App:** https://anchor-topaz.vercel.app/


*Rewrite your story. Protect it when it matters.*
