# AI Construction Task Manager

## Setup
1. Clone repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` with `GENAI_API_KEY=your_api_key`
4. Run: `uvicorn app.main:app --reload`

## Testing
Run all tests:
```bash
PYTHONPATH=. pytest tests/ -v
```


## API Endpoints
- POST `/projects/`: Create new project
- GET `/projects/{id}`: Get project statu

Example:
```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"project_name": "Office Building", "location": "New York"}' \
http://localhost:8000/projects/
