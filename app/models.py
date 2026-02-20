# app/models.py
"""
Pydantic models for request/response validation.
GitHub-ready: keep schemas centralized here.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class TicketCreate(BaseModel):
    source: str = Field(..., examples=["zapier", "web", "email"])
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)


class TicketOut(BaseModel):
    id: int
    source: str
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    subject: str
    body: str
    status: str
    priority: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    suggested_reply: Optional[str] = None
    created_at: str
    updated_at: str

from typing import Literal

class TicketUpdate(BaseModel):
    status: Literal["new", "open", "pending", "resolved", "closed"] | None = None
    priority: Literal["low", "medium", "high"] | None = None
    category: Literal["billing", "technical", "account", "other"] | None = None
    summary: str | None = None
    suggested_reply: str | None = None
