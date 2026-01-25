from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()


from fastapi import FastAPI

# --- Auth-firebase routers ---
from api import journal, safety, crisis, notifications, wrapped
from api.auth import router as auth_router  # newly created auth endpoints

# --- api_core routers (unique ones) ---
from api.dashboard import router as dashboard_router
from api.community import router as community_router


app = FastAPI(title="Anchor Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include routers ---
# Firebase auth + main routes
app.include_router(auth_router)
app.include_router(journal.router)
app.include_router(safety.router)
app.include_router(crisis.router)
app.include_router(notifications.router)
app.include_router(wrapped.router)


# api_core unique routes
app.include_router(dashboard_router)
app.include_router(community_router)

# --- Root & health endpoints ---
@app.get("/")
def read_root():
    return {"message": "Anchor backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

