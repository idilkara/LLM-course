# Microblogging Web Application Requirements

## Features
- User profile creation
- User login/authentication
- Post short text updates (max 280 characters)
- View global chronological feed of all posts
- Like posts
- Reply to posts (one level deep)
- View user profiles and their posts

## Constraints
- No private messaging
- No retweets/reposts
- No follower graph (global feed only)

## Tech Stack
- Backend: PYTHON
- Frontend: HTML-JS
- Database: SQLite (for simplicity)
- Auth: JWT-based
- Logging: Python logging module
- Testing: Pytest (backend), Jest (frontend)

## Non-Functional Requirements
- High performance and responsiveness
- Clean, maintainable code
- Comprehensive tests
- Logging for key actions

## Directory Structure
- backend/: FastAPI app, models, tests, logs
- frontend/: React app, components, tests
- .github/: copilot-instructions.md

## Next Steps
- Scaffold backend and frontend
- Implement features
- Add tests and logging
- Document project
