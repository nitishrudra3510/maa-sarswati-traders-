Demo Script

Self-intro (30s)
- Name, role, project purpose: deliver personalized video recommendations via FastAPI API.

Technical demo (3–5 min)
- Start server: `uvicorn app.main:app --reload`
- Show Swagger at `/docs`.
- Postman calls:
  - `GET /feed?username=testuser`
  - `GET /feed?username=testuser&project_code=fitness`
- Explain logic: cold start -> recent posts; personalized -> cosine similarity over content vectors; category -> filter.
- Show caching: second call is faster (Redis).
- Show pagination: `limit` and `offset`.

Cold start example
- New user with no engagements returns default recent posts with reason `cold_start`.


