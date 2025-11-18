import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import Wallet, Transaction

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Crypto Dashboard Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response

# Utility to ensure a wallet exists for given owner
async def ensure_wallet(owner: str = "default") -> dict:
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    # Upsert a wallet with default values if it doesn't exist
    db["wallet"].update_one(
        {"owner": owner},
        {"$setOnInsert": {"owner": owner, "balance": 0.0, "currency": "USD"}},
        upsert=True,
    )
    doc = db["wallet"].find_one({"owner": owner})
    return doc

class AmountRequest(BaseModel):
    amount: float
    owner: str = "default"
    note: str | None = None

@app.get("/api/wallet")
async def get_wallet(owner: str = "default"):
    doc = await ensure_wallet(owner)
    if not doc:
        raise HTTPException(status_code=404, detail="Wallet not found")
    doc["_id"] = str(doc.get("_id")) if doc.get("_id") else None
    return doc

@app.get("/api/transactions")
async def list_transactions(owner: str = "default", limit: int = 50):
    txs = get_documents("transaction", {"owner": owner}, limit=limit)
    # Sort newest first
    txs = sorted(txs, key=lambda x: x.get("created_at", 0), reverse=True)
    for t in txs:
        if t.get("_id"): t["_id"] = str(t["_id"])
    return txs

@app.post("/api/deposit")
async def deposit(req: AmountRequest):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    wallet = await ensure_wallet(req.owner)
    new_balance = float(wallet.get("balance", 0)) + float(req.amount)
    db["wallet"].update_one({"owner": req.owner}, {"$set": {"balance": new_balance}})

    tx = Transaction(owner=req.owner, type="deposit", amount=req.amount, balance_after=new_balance, note=req.note)
    create_document("transaction", tx)
    return {"success": True, "balance": new_balance}

@app.post("/api/withdraw")
async def withdraw(req: AmountRequest):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    wallet = await ensure_wallet(req.owner)
    current = float(wallet.get("balance", 0))
    if req.amount > current:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    new_balance = current - float(req.amount)
    db["wallet"].update_one({"owner": req.owner}, {"$set": {"balance": new_balance}})

    tx = Transaction(owner=req.owner, type="withdrawal", amount=req.amount, balance_after=new_balance, note=req.note)
    create_document("transaction", tx)
    return {"success": True, "balance": new_balance}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
