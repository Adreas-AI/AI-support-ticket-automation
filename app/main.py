"""
FastAPI entrypoint for AI Support Ticket Automation.
"""

from typing import List

from fastapi import FastAPI, HTTPException, Query

from app.ai import analyze_ticket
from app.db import get_connection, init_db
from app.models import TicketCreate, TicketOut, TicketUpdate
from app.rabbitmq_client import send_message


app = FastAPI(
    title="AI Support Ticket Automation API",
    version="0.1.0"
)


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "AI Support Ticket Automation API"
    }


@app.post("/tickets", response_model=TicketOut)
def create_ticket(ticket: TicketCreate):
    print("create_ticket hit")

    # ---- AI analysis ----
    try:
        ai_data = analyze_ticket(ticket.subject, ticket.body)
    except Exception:
        ai_data = {
            "priority": None,
            "category": None,
            "summary": None,
            "suggested_reply": None,
        }

    # ---- DB insert ----
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tickets (
                source,
                customer_name,
                customer_email,
                subject,
                body,
                priority,
                category,
                summary,
                suggested_reply
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket.source,
                ticket.customer_name,
                ticket.customer_email,
                ticket.subject,
                ticket.body,
                ai_data.get("priority"),
                ai_data.get("category"),
                ai_data.get("summary"),
                ai_data.get("suggested_reply"),
            ),
        )

        ticket_id = cursor.lastrowid

        row = conn.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,),
        ).fetchone()

    # 👇 ΕΔΩ είναι σωστά το RabbitMQ
    send_message({
        "ticket_id": ticket_id,
        "subject": ticket.subject,
        "body": ticket.body,
        "email": ticket.customer_email
    })

    return dict(row)


@app.get("/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return dict(row)


@app.get("/tickets", response_model=List[TicketOut])
def list_tickets(
    status: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = "SELECT * FROM tickets"
    params: list = []

    if status:
        query += " WHERE status = ?"
        params.append(status)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_connection() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()

    return [dict(r) for r in rows]


@app.patch("/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, patch: TicketUpdate):
    updates = []
    params = []

    data = patch.model_dump(exclude_unset=True)
    for key, value in data.items():
        updates.append(f"{key} = ?")
        params.append(value)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided")

    params.append(ticket_id)

    with get_connection() as conn:
        cur = conn.execute(
            f"UPDATE tickets SET {', '.join(updates)} WHERE id = ?",
            tuple(params),
        )

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ticket not found")

        row = conn.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,),
        ).fetchone()

    return dict(row)

