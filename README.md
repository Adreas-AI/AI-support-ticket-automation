# 🤖 AI Support Ticket Automation System

This project is a backend system built with FastAPI that automates the processing of customer support tickets using AI. When a ticket is created, it is immediately stored and then sent to a RabbitMQ queue for asynchronous processing by a background worker. The worker uses AI to analyze the ticket content and generates structured insights such as category, priority level, a short summary, and a suggested reply to the customer. All results are saved in a SQLite database and can be retrieved or updated through REST API endpoints. The system is designed with a clean, modular architecture and demonstrates real-world backend engineering concepts such as event-driven processing, message queues, and AI-powered automation.

Run locally:
python -m uvicorn app.main:app --reload


API docs available at:
http://127.0.0.1:8000/docs



