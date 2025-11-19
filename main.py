import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from database import db, create_document, get_documents
from schemas import Owner, Property, Unit, Tenant, UtilityInvoice, Bill

app = FastAPI(title="Real Estate Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Real Estate Management API is running"}


@app.get("/schema")
def get_schema_models():
    # Expose schema class names so the viewer can pick them up
    return {
        "models": [
            "owner",
            "property",
            "unit",
            "tenant",
            "utilityinvoice",
            "bill",
        ]
    }


# Basic CRUD helpers
class IdRequest(BaseModel):
    id: str


@app.post("/owners")
def create_owner(owner: Owner):
    try:
        inserted_id = create_document("owner", owner)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/owners")
def list_owners(limit: Optional[int] = 50):
    try:
        docs = get_documents("owner", limit=limit)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/properties")
def create_property(prop: Property):
    try:
        inserted_id = create_document("property", prop)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/properties")
def list_properties(limit: Optional[int] = 50, owner_id: Optional[str] = None):
    try:
        filter_dict: Dict[str, Any] = {}
        if owner_id:
            filter_dict["owner_id"] = owner_id
        docs = get_documents("property", filter_dict, limit)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/units")
def create_unit(unit: Unit):
    try:
        inserted_id = create_document("unit", unit)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/units")
def list_units(limit: Optional[int] = 50, property_id: Optional[str] = None):
    try:
        filter_dict: Dict[str, Any] = {}
        if property_id:
            filter_dict["property_id"] = property_id
        docs = get_documents("unit", filter_dict, limit)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tenants")
def create_tenant(tenant: Tenant):
    try:
        inserted_id = create_document("tenant", tenant)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tenants")
def list_tenants(limit: Optional[int] = 50, property_id: Optional[str] = None, unit_id: Optional[str] = None):
    try:
        filter_dict: Dict[str, Any] = {}
        if property_id:
            filter_dict["property_id"] = property_id
        if unit_id:
            filter_dict["unit_id"] = unit_id
        docs = get_documents("tenant", filter_dict, limit)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/utility_invoices")
def create_utility_invoice(inv: UtilityInvoice):
    try:
        inserted_id = create_document("utilityinvoice", inv)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/utility_invoices")
def list_utility_invoices(limit: Optional[int] = 50, property_id: Optional[str] = None):
    try:
        filter_dict: Dict[str, Any] = {}
        if property_id:
            filter_dict["property_id"] = property_id
        docs = get_documents("utilityinvoice", filter_dict, limit)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/bills")
def create_bill(bill: Bill):
    try:
        inserted_id = create_document("bill", bill)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/bills")
def list_bills(limit: Optional[int] = 50, tenant_id: Optional[str] = None, property_id: Optional[str] = None, period: Optional[str] = None):
    try:
        filter_dict: Dict[str, Any] = {}
        if tenant_id:
            filter_dict["tenant_id"] = tenant_id
        if property_id:
            filter_dict["property_id"] = property_id
        if period:
            filter_dict["period"] = period
        docs = get_documents("bill", filter_dict, limit)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Simple text parser for utility invoices
class ParseRequest(BaseModel):
    text: str


@app.post("/parse_utility")
def parse_utility(req: ParseRequest):
    """
    Very simple parser that extracts totals for water, electricity, and gas
    by scanning for patterns like "Water: 123.45" (case-insensitive).
    """
    text = req.text or ""
    lowered = text.lower()
    totals: Dict[str, float] = {}

    import re

    def find_amount(label: str):
        pattern = rf"{label}\s*[:\-]?\s*\$?\s*([0-9]+(?:\.[0-9]{1,2})?)"
        m = re.search(pattern, lowered, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except Exception:
                return None
        return None

    for label in ["water", "electric", "electricity", "power", "gas", "sewer", "trash"]:
        amt = find_amount(label)
        if amt is not None:
            key = "electricity" if label in ["electric", "power", "electricity"] else label
            totals[key] = amt

    return {"totals": totals, "found": list(totals.keys())}


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
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
