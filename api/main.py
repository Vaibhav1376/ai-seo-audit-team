from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import os
import time
from datetime import datetime
import sqlite3

app = FastAPI(title="SEO Audit API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database for API keys and usage
def init_db():
    conn = sqlite3.connect("api_usage.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            api_key TEXT PRIMARY KEY,
            tier TEXT NOT NULL,
            requests_limit INTEGER,
            requests_used INTEGER DEFAULT 0,
            created_at TEXT,
            last_used TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT,
            endpoint TEXT,
            timestamp TEXT,
            response_time REAL,
            status INTEGER
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

# Tiers
TIERS = {
    "free": {"limit": 10, "price": 0},
    "pro": {"limit": 100, "price": 49},
    "enterprise": {"limit": 1000, "price": 199}
}

# Request models
class AuditRequest(BaseModel):
    url: str
    niche: Optional[str] = "general"
    features: Optional[Dict] = {}

class APIKeyCreate(BaseModel):
    email: str
    tier: str = "free"

# API Key validation
async def verify_api_key(x_api_key: str = Header(...)):
    conn = sqlite3.connect("api_usage.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT tier, requests_limit, requests_used FROM api_keys WHERE api_key = ?", (x_api_key,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    tier, limit, used = result
    
    if used >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return {"api_key": x_api_key, "tier": tier, "used": used, "limit": limit}

# Endpoints
@app.post("/api/v1/audit")
async def audit_page(
    request: AuditRequest,
    api_key_info: dict = Depends(verify_api_key)
):
    """Run SEO audit"""
    start_time = time.time()
    
    try:
        # Import your workflow
        from workflows import run_single_page_audit
        
        report, auditdata, serpdata = run_single_page_audit(
            request.url,
            request.niche,
            features=request.features
        )
        
        # Update usage
        update_usage(api_key_info["api_key"], "/api/v1/audit", time.time() - start_time, 200)
        
        return {
            "success": True,
            "url": request.url,
            "scores": auditdata.get("scores", {}),
            "report": report,
            "usage": {
                "used": api_key_info["used"] + 1,
                "limit": api_key_info["limit"],
                "remaining": api_key_info["limit"] - api_key_info["used"] - 1
            }
        }
        
    except Exception as e:
        update_usage(api_key_info["api_key"], "/api/v1/audit", time.time() - start_time, 500)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/keys")
async def create_api_key(request: APIKeyCreate):
    """Create new API key"""
    import secrets
    
    if request.tier not in TIERS:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    api_key = f"seo_{secrets.token_urlsafe(32)}"
    
    conn = sqlite3.connect("api_usage.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO api_keys (api_key, tier, requests_limit, created_at)
        VALUES (?, ?, ?, ?)
    """, (api_key, request.tier, TIERS[request.tier]["limit"], datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return {
        "api_key": api_key,
        "tier": request.tier,
        "limit": TIERS[request.tier]["limit"],
        "price": TIERS[request.tier]["price"]
    }

@app.get("/api/v1/usage")
async def get_usage(api_key_info: dict = Depends(verify_api_key)):
    """Get API usage stats"""
    
    conn = sqlite3.connect("api_usage.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*), AVG(response_time)
        FROM api_requests
        WHERE api_key = ?
    """, (api_key_info["api_key"],))
    
    total, avg_time = cursor.fetchone()
    conn.close()
    
    return {
        "tier": api_key_info["tier"],
        "total_requests": total or 0,
        "avg_response_time": round(avg_time or 0, 2),
        "used": api_key_info["used"],
        "limit": api_key_info["limit"],
        "remaining": api_key_info["limit"] - api_key_info["used"]
    }

def update_usage(api_key: str, endpoint: str, response_time: float, status: int):
    """Update usage stats"""
    conn = sqlite3.connect("api_usage.db")
    cursor = conn.cursor()
    
    # Increment usage
    cursor.execute("UPDATE api_keys SET requests_used = requests_used + 1, last_used = ? WHERE api_key = ?",
                   (datetime.now().isoformat(), api_key))
    
    # Log request
    cursor.execute("""
        INSERT INTO api_requests (api_key, endpoint, timestamp, response_time, status)
        VALUES (?, ?, ?, ?, ?)
    """, (api_key, endpoint, datetime.now().isoformat(), response_time, status))
    
    conn.commit()
    conn.close()

# Health check
@app.get("/")
async def root():
    return {"status": "online", "version": "1.0.0"}
