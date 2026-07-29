# Stock Intelligence Platform

A from-scratch stock research and portfolio intelligence platform for
long-term investors.

The project is being built incrementally as a learning project. Milestone 1
established the Next.js and FastAPI foundations. Milestone 2 adds a responsive
frontend dashboard backed entirely by typed static mock data.

## Technology

- **Frontend:** Next.js, TypeScript, Tailwind CSS
- **Backend:** Python, FastAPI
- **Database:** none required yet; PostgreSQL is planned for a later milestone
- **Data sources:** free SEC EDGAR and free market-data APIs in later milestones

All required tools and services must remain free.

## Repository Layout

```text
.
├── frontend/          Next.js browser application
├── backend/           FastAPI HTTP API and backend tests
├── AGENTS.md          durable project and collaboration instructions
├── README.md          setup and development guide
└── .gitignore         generated and local-only files excluded from Git
```

## Prerequisites

- Git
- Node.js 20.9 or newer and npm
- Python 3.11 or newer
- Windows PowerShell

The commands below assume PowerShell. This machine's PowerShell execution
policy blocks the `npm.ps1` shim, so the examples use `npm.cmd`, which invokes
the same npm installation.

## Run the Frontend

```powershell
Set-Location .\frontend
npm.cmd install
npm.cmd run dev
```

Open <http://localhost:3000>. The frontend health endpoint is available at
<http://localhost:3000/api/health>.

## Run the Backend

The Python environment is intentionally not stored in Git. Create it and
install the backend packages once:

```powershell
Set-Location .\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Then, in a second PowerShell terminal:

```powershell
Set-Location .\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

If local PowerShell policy prevents activation, activation is optional. Run
the environment's interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open <http://localhost:8000>. The API health endpoint is available at
<http://localhost:8000/health>, and FastAPI's interactive API documentation is
at <http://localhost:8000/docs>.

## Validation Commands

Frontend:

```powershell
Set-Location .\frontend
npm.cmd run lint
npm.cmd run build
```

Backend:

```powershell
Set-Location .\backend
.\.venv\Scripts\python.exe -m pytest
```

## Milestone Status

- [x] Milestone 1: repository and application foundations
- [x] Milestone 2: responsive frontend dashboard with typed static mock data
- [ ] Watchlist and market-data milestones
- [ ] Portfolio transactions and return calculations
- [ ] Fundamental analysis and SEC filing retrieval
- [ ] Thesis tracking and evidence comparison
- [ ] Valuation scenarios and local AI-assisted analysis
