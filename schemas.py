"""
Database Schemas for Real Estate Management SaaS

Each Pydantic model below represents a MongoDB collection. The collection name
is the lowercase of the class name (e.g., Property -> "property").

These schemas are used by the database viewer and can also be imported by the API
for validation.
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class Owner(BaseModel):
    name: str = Field(..., description="Full name of the property owner")
    email: str = Field(..., description="Email address of the owner")
    phone: Optional[str] = Field(None, description="Contact phone number")


class Property(BaseModel):
    owner_id: str = Field(..., description="Reference to the owner (string ObjectId)")
    name: str = Field(..., description="Property name or label")
    address: str = Field(..., description="Street address")
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


class Unit(BaseModel):
    property_id: str = Field(..., description="Reference to the property (string ObjectId)")
    unit_number: str = Field(..., description="Unit/Apartment number or label")
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[float] = Field(None, ge=0)
    square_feet: Optional[int] = Field(None, ge=0)
    tenant_id: Optional[str] = Field(None, description="Reference to current tenant (string ObjectId)")


class Tenant(BaseModel):
    property_id: str = Field(..., description="Reference to the property (string ObjectId)")
    unit_id: Optional[str] = Field(None, description="Reference to the unit (string ObjectId)")
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    lease_start: Optional[str] = Field(None, description="Lease start date (YYYY-MM-DD)")
    lease_end: Optional[str] = Field(None, description="Lease end date (YYYY-MM-DD)")
    monthly_rent: Optional[float] = Field(None, ge=0)


class UtilityInvoice(BaseModel):
    property_id: str = Field(..., description="Reference to the property (string ObjectId)")
    period_start: Optional[str] = Field(None, description="YYYY-MM-DD")
    period_end: Optional[str] = Field(None, description="YYYY-MM-DD")
    vendor: Optional[str] = Field(None, description="Name of utility vendor (e.g., City Water)")
    raw_text: Optional[str] = Field(None, description="Raw invoice text used for parsing")
    totals: Dict[str, float] = Field(default_factory=dict, description="Parsed totals per utility type, e.g., {water: 123.45}")


class Bill(BaseModel):
    tenant_id: str = Field(..., description="Reference to tenant (string ObjectId)")
    unit_id: str = Field(..., description="Reference to unit (string ObjectId)")
    property_id: str = Field(..., description="Reference to property (string ObjectId)")
    period: str = Field(..., description="Billing period label, e.g., 2025-01")
    items: List[Dict[str, float]] = Field(default_factory=list, description="List of charges as {label: amount}")
    total: float = Field(..., ge=0)
    status: str = Field("unpaid", description="unpaid | paid | partial")
