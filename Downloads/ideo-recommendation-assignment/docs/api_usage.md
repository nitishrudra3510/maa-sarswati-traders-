API Usage

Feed
```bash
curl -s "http://localhost:8000/feed?username=testuser"
curl -s "http://localhost:8000/feed?username=testuser&project_code=fitness"
curl -s "http://localhost:8000/feed?username=testuser&limit=10&offset=20"
```

Run server
```bash
uvicorn app.main:app --reload
```


