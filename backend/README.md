# Backend Setup

## Requirements
- Python 3.9+
- FastAPI
- Uvicorn
- SQLAlchemy
- Passlib
- PyJWT
- pytest

## Install dependencies
```bash
pip install fastapi uvicorn sqlalchemy passlib[bcrypt] pyjwt pytest
```

## Run the server
```bash
uvicorn main:app --reload
```

## Run tests
```bash
pytest
```
