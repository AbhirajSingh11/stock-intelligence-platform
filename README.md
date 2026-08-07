# Stock Intelligence Platform

A from-scratch stock research and portfolio intelligence platform for
long-term investors.

The project is being built incrementally as a learning project. Milestone 1
established the Next.js and FastAPI foundations. Milestone 2 adds a responsive
frontend dashboard. Milestone 3 moves dashboard data ownership to FastAPI and
establishes a typed frontend-to-backend data flow. Milestone 4 adds official
SEC EDGAR company search, company profiles, and recent filing history.
Milestone 5 adds normalized annual and quarterly company fundamentals from the
official SEC Company Facts API.

## Technology

- **Frontend:** Next.js, TypeScript, Tailwind CSS
- **Backend:** Python, FastAPI
- **Database:** none required yet; PostgreSQL is planned for a later milestone
- **Data sources:** official, free SEC EDGAR JSON endpoints; market data comes
  in a later milestone

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

Install frontend packages once:

```powershell
Set-Location .\frontend
npm.cmd install
```

The browser-visible API base URL defaults to `http://127.0.0.1:8000`. To make
that configuration explicit, copy the committed example file:

```powershell
Copy-Item .env.example .env.local
```

Then start Next.js:

```powershell
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

Start FastAPI:

```powershell
Set-Location .\backend
.\.venv\Scripts\Activate.ps1
$env:SEC_USER_AGENT = "Stock Intelligence Platform your-email@example.com"
python -m uvicorn app.main:app --reload
```

If local PowerShell policy prevents activation, activation is optional. Run
the environment's interpreter directly:

```powershell
$env:SEC_USER_AGENT = "Stock Intelligence Platform your-email@example.com"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Replace `your-email@example.com` with a monitored contact address before
making live SEC requests. This value identifies the application to the SEC; it
is not a secret and is not sent to the browser.

Open <http://localhost:8000>. The API health endpoint is available at
<http://localhost:8000/health>, and FastAPI's interactive API documentation is
at <http://localhost:8000/docs>.

The dashboard overview endpoint is:

<http://127.0.0.1:8000/api/v1/dashboard/overview>

The Milestone 4 company endpoints are:

- `GET /api/v1/companies/search?query=Microsoft&limit=8`
- `GET /api/v1/companies/MSFT`
- `GET /api/v1/companies/MSFT/filings?forms=10-K,10-Q,8-K&limit=20`

The Milestone 5 fundamentals endpoint is:

- `GET /api/v1/companies/MSFT/fundamentals`

Search requires at least two non-whitespace characters. Search limits range
from 1 to 20. Filing limits range from 1 to 100, and `forms` accepts up to ten
unique comma-separated SEC form names.

## Local Environment Variables

Frontend (`frontend/.env.local`):

```dotenv
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

`NEXT_PUBLIC_API_BASE_URL` is embedded into browser JavaScript when Next.js
starts or builds. Restart the frontend after changing it.

Backend:

```dotenv
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
SEC_USER_AGENT=Stock Intelligence Platform contact@example.com
```

FastAPI uses those two explicit local origins by default, so no backend
environment file is required for CORS. `SEC_USER_AGENT` is required only for
the SEC-backed company endpoints; dashboard and health endpoints remain
available without it. To use `backend/.env.example`, copy it to
`backend/.env`, replace the placeholder contact, and add `--env-file .env` to
the Uvicorn command:

```powershell
Set-Location .\backend
Copy-Item .env.example .env
# Edit .env and replace contact@example.com before continuing.
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --env-file .env
```

The example also documents optional SEC timeout, rate, and cache settings.
Wildcard CORS origins are rejected, and the application will reject an SEC
rate setting above 5 requests per second.

## Local Service Start Order

1. Start FastAPI on port 8000.
2. Start Next.js on port 3000 in a second terminal.
3. Open <http://localhost:3000>.

Starting FastAPI first lets the initial dashboard request succeed immediately.
If FastAPI is unavailable, the frontend displays a connection error and a
Retry button.

Use the header search field to enter at least two ticker or company-name
characters. Results come from the SEC ticker mapping. Select a result with the
mouse or the arrow keys and Enter to open `/companies/[ticker]`.

Dashboard values remain deterministic, backend-owned mock data during
Milestone 5. Official SEC data is used for company search, profiles, recent
filing history, and standardized company fundamentals. There is still no
database or market-data provider.

## SEC EDGAR Usage

Company data is attributed to the
[U.S. Securities and Exchange Commission](https://www.sec.gov/edgar/sec-api-documentation).
The backend calls only the official SEC ticker mapping, submissions JSON, and
Company Facts JSON endpoints. Filing and fact-provenance links lead directly
to `sec.gov`.

The SEC allows no more than 10 requests per second. This application uses a
stricter maximum of 5 requests per second, reuses one HTTP connection pool,
and retries only a bounded number of transient failures. Successful ticker
mapping responses are cached in memory for 24 hours; company submissions and
Company Facts are cached for 15 minutes. Concurrent cache misses are
coalesced. One Company Facts response supplies every supported metric for a
company; the backend does not make one SEC request per metric. The cache is
local to the FastAPI process and resets when that process restarts.

### Standardized Fundamentals

Milestone 5 supports revenue, operating income, net income, diluted EPS, cash
and cash equivalents, long-term debt, operating margin, and net margin. A
central registry records each metric's accepted taxonomy, tags, unit, fact
type, forms, and any permitted formula.

Primary revenue uses
`RevenueFromContractWithCustomerExcludingAssessedTax`; `Revenues` and
`SalesRevenueNet` are ordered fallbacks. Net income uses `NetIncomeLoss`, with
`ProfitLoss` as a fallback. Long-term debt uses `LongTermDebt` directly when
available. Its only derived fallback is the exact sum of
`LongTermDebtCurrent` and `LongTermDebtNoncurrent` from the same period and
filing. It does not combine leases, short-term borrowings, total liabilities,
or unrelated debt concepts. Operating and net margins are derived only when
the numerator and revenue share exact period boundaries and filing
provenance.

Annual duration series accept fiscal-year 10-K or 10-K/A observations with a
defensible annual duration. Quarterly duration series accept only 10-Q or
10-Q/A observations explicitly framed by the SEC as a discrete quarter;
unframed year-to-date values are rejected, and Q4 is not invented from annual
data. Instant facts are deduplicated by period end and may come from 10-Q or
10-K filings. Series retain at most five annual and eight quarterly periods.
Values selected from amended filings, fallback concepts, or formulas are
identified in the response and UI.

Missing, malformed, incompatible-unit, or unsupported concepts produce an
unavailable metric or data-quality warning rather than a fabricated zero.
Every returned fact includes its taxonomy tag, accession number, filing date,
and direct SEC filing URL. The response also links to the original Company
Facts resource.

Standardized XBRL still has important limitations: companies may choose
different concepts, historical taxonomy usage can change, SEC frames are not
available for every observation, fiscal calendars do not always align to
calendar quarters, and amended filings can restate earlier values. The
normalizer intentionally returns gaps when it cannot establish compatible
units, periods, or provenance.

The backend pins `httpx==0.28.1` because the SEC integration needs an
asynchronous HTTP client with connection pooling, separate timeouts, and a
mockable transport. No frontend dependency was added.

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
.\.venv\Scripts\python.exe -m pip check
```

## Milestone Status

- [x] Milestone 1: repository and application foundations
- [x] Milestone 2: responsive frontend dashboard with typed static mock data
- [x] Milestone 3: typed FastAPI-to-frontend dashboard data flow
- [x] Milestone 4: SEC EDGAR company search, profiles, and recent filings
- [x] Milestone 5: SEC Company Facts financial trends and provenance
- [ ] Watchlist and market-data milestones
- [ ] Portfolio transactions and return calculations
- [ ] Deeper fundamental analysis and SEC filing-document retrieval
- [ ] Thesis tracking and evidence comparison
- [ ] Valuation scenarios and local AI-assisted analysis
