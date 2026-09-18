# Project Context

**Last synced:** 2026-09-17 21:45:55
**Branch:** master

## Project Structure
```
.
./.dockerignore
./.env
./.env.example
./.git
./.github
./.github/workflows
./.github/workflows/ci.yml
./.gitignore
./.pytest_cache
./.pytest_cache/.gitignore
./.pytest_cache/CACHEDIR.TAG
./.pytest_cache/README.md
./.pytest_cache/v
./.pytest_cache/v/cache
./.pytest_cache/v/cache/lastfailed
./.pytest_cache/v/cache/nodeids
./.pytest_cache/v/cache/stepwise
./.venv
./.vscode
./Dockerfile
./README.md
./__pycache__
./__pycache__/config.cpython-312.pyc
./app
./app/__init__.py
./app/__pycache__
./app/__pycache__/__init__.cpython-312.pyc
./app/__pycache__/models.cpython-312.pyc
./app/jobs
./app/jobs/__init__.py
./app/jobs/__pycache__
./app/jobs/__pycache__/__init__.cpython-312.pyc
./app/jobs/__pycache__/scheduler.cpython-312.pyc
./app/jobs/scheduler.py
./app/models.py
./app/routes
./app/routes/__init__.py
./app/routes/__pycache__
./app/routes/__pycache__/__init__.cpython-312.pyc
./app/routes/__pycache__/api.cpython-312.pyc
./app/routes/__pycache__/dashboard.cpython-312.pyc
./app/routes/__pycache__/games.cpython-312.pyc
./app/routes/api.py
./app/routes/dashboard.py
./app/routes/games.py
./app/services
./app/services/__init__.py
./app/services/__pycache__
./app/services/__pycache__/__init__.cpython-312.pyc
./app/services/__pycache__/analyzer.cpython-312.pyc
./app/services/__pycache__/normalizer.cpython-312.pyc
./app/services/__pycache__/odds_fetcher.cpython-312.pyc
./app/services/__pycache__/odds_insights.cpython-312.pyc
./app/services/analyzer.py
./app/services/normalizer.py
./app/services/odds_fetcher.py
./app/services/odds_insights.py
./app/static
./app/static/js
```

## Recent Commits
```
09db58e Update last synced timestamp in claude.md and remove _private_demo_seed.py from project structure
8471979 Add demo mode configuration to .env.example, update app initialization to enforce scheduler settings, and introduce seed_demo.py for demo data population. Update README with demo usage instructions and add render.yaml for deployment configuration.
23cd708 Add claude.md for project context and structure, update .gitignore to exclude _private_demo_seed.py, and remove CI badge from README.md
feaa035 Remove game pinning feature and related code, update dashboard and game detail templates accordingly, and clean up unused imports and functions.
7424bee Load environment variables before importing Config in app initialization
b8ed462 Add Docker support with Dockerfile and docker-compose.yml, create .dockerignore and .env.example files, and update README for setup instructions
e9ca38c Add configuration for fetch intervals, steam detection, and implement pinning feature for games
375858e Restructure project layout
507942b Initial commit
```

## Notes
<!-- Add persistent project context here -->
