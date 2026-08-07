# Stock Intelligence Platform

A from-scratch stock research and portfolio intelligence platform for
long-term investors.

The project is being built incrementally as a learning project. Milestone 1
established the Next.js and FastAPI foundations. Milestone 2 adds a responsive
frontend dashboard. Milestone 3 moves dashboard data ownership to FastAPI and
establishes a typed frontend-to-backend data flow. Milestone 4 adds official
SEC EDGAR company search, company profiles, and recent filing history.
Milestone 5 adds normalized annual and quarterly company fundamentals from the
official SEC Company Facts API. Milestone 6 adds the first durable application
state: a single-user watchlist stored locally in SQLite through SQLAlchemy and
versioned Alembic migrations. Milestone 7 adds persistent buy/sell
transactions, Decimal-based weighted-average accounting, manual price marks,
and real portfolio intelligence on both `/portfolio` and the dashboard.

## Technology

- **Frontend:** Next.js, TypeScript, Tailwind CSS
- **Backend:** Python, FastAPI
- **Database:** SQLite for local development; PostgreSQL is planned for a later milestone
- **Data sources:** official, free SEC EDGAR JSON endpoints; portfolio prices
  are entered manually because live market data remains out of scope

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
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

If local PowerShell policy prevents activation, activation is optional. Run
the environment's interpreter directly:

```powershell
$env:SEC_USER_AGENT = "Stock Intelligence Platform your-email@example.com"
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Run the migration before the first server start and after pulling any new
migration. FastAPI intentionally does not create or alter tables at startup.

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

The Milestone 6 watchlist endpoints are:

- `GET /api/v1/watchlist`
- `POST /api/v1/watchlist` with JSON such as `{ "ticker": "MSFT" }`
- `DELETE /api/v1/watchlist/MSFT`

The Milestone 7 portfolio endpoints are:

- `GET /api/v1/portfolio/overview`
- `GET /api/v1/portfolio/transactions` with optional `?ticker=MSFT`
- `POST /api/v1/portfolio/transactions`
- `PATCH /api/v1/portfolio/transactions/{transaction_id}`
- `DELETE /api/v1/portfolio/transactions/{transaction_id}`
- `PUT /api/v1/portfolio/marks/{ticker}`

Transaction creates accept `ticker`, `side`, `trade_date`, `quantity`,
`price_per_share`, `fees`, and optional `notes`. The first transaction for a
security resolves its official ticker, ten-digit CIK, and company name through
the SEC company service. Later transactions reuse that stored identity. All
financial values are serialized as exact decimal strings; dates and timestamps
use ISO formats.

Creates resolve the ticker through the official SEC mapping before storing its
normalized ticker, ten-digit CIK, and official company name. A duplicate create
returns `409 watchlist_entry_exists`; deleting an absent ticker returns
`404 watchlist_entry_not_found`.

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
DATABASE_URL=sqlite+aiosqlite:///./data/stock-intelligence.db
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

`DATABASE_URL` is optional; the value above is the safe default when commands
run from `backend/`. It creates `backend/data/stock-intelligence.db`, which is
local runtime data and ignored by Git. When selecting a different database,
set `DATABASE_URL` in the PowerShell session before running both Alembic and
Uvicorn. The example also documents optional SEC timeout, rate, and cache settings.
Wildcard CORS origins are rejected, and the application will reject an SEC
rate setting above 5 requests per second.

`SEC_USER_AGENT` is also required when the first transaction for a new
portfolio ticker is created, because that operation stores the official SEC
identity. Once that identity exists in the ledger, later transactions reuse it
without another SEC ticker-mapping request.

## Local Service Start Order

1. From `backend/`, run `.\.venv\Scripts\python.exe -m alembic upgrade head`.
2. Start FastAPI on port 8000.
3. Start Next.js on port 3000 in a second terminal.
4. Open <http://localhost:3000>.

Starting FastAPI first lets the initial dashboard request succeed immediately.
If FastAPI is unavailable, the frontend displays a connection error and a
Retry button.

Use the header search field to enter at least two ticker or company-name
characters. Results come from the SEC ticker mapping. Select a result with the
mouse or the arrow keys and Enter to open `/companies/[ticker]`.

Portfolio values now come from the persisted transaction ledger and manual
price marks. The former mock portfolio summary and mock performance history
have been removed; without historical prices, the application does not claim
historical portfolio performance. Thesis signals remain deterministic,
backend-owned mock data during Milestone 7. The watchlist remains stored in
SQLite and is loaded through its own API.
Official SEC data is used for company search, profiles, recent filing history,
standardized company fundamentals, and watchlist identity validation. There is
still no market-data provider. Watchlist cards do not claim prices or position
values, and every portfolio mark is visibly labeled as manual rather than live.

## Local Database and Migrations

SQLAlchemy 2.x provides typed models, an async engine, and request-scoped
sessions. `aiosqlite` is the local async driver. Alembic owns every schema
change. The route, service, repository, schema, model, and database lifecycle
layers are kept separate so HTTP details do not leak into persistence code.

Useful migration commands, run from `backend/`, are:

```powershell
# Apply every pending migration.
.\.venv\Scripts\python.exe -m alembic upgrade head

# Show the revision currently applied to the local database.
.\.venv\Scripts\python.exe -m alembic current

# Revert the most recent migration during development.
.\.venv\Scripts\python.exe -m alembic downgrade -1
```

Before a backup or reset, stop FastAPI so SQLite has no pending write-ahead-log
state. To back up the default local database, copy its main file after the
server has stopped:

```powershell
Set-Location .\backend
New-Item -ItemType Directory -Force .\backups
Copy-Item .\data\stock-intelligence.db .\backups\stock-intelligence-$(Get-Date -Format yyyyMMdd-HHmmss).db
```

The copied file contains both watchlist and portfolio records. Keep backups
outside the repository if they contain sensitive personal information.

To intentionally reset only the default local development database, first
stop FastAPI, then run:

```powershell
Set-Location .\backend
Remove-Item -LiteralPath .\data\stock-intelligence.db -ErrorAction SilentlyContinue
Remove-Item -LiteralPath .\data\stock-intelligence.db-shm -ErrorAction SilentlyContinue
Remove-Item -LiteralPath .\data\stock-intelligence.db-wal -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -m alembic upgrade head
```

This permanently removes the local watchlist, transactions, and manual price
marks. Migrations and test fixtures are versioned and are not deleted.
Automated tests override `DATABASE_URL` with a fresh SQLite file under pytest's
temporary directory, migrate it, and release all connections during cleanup;
they never use the developer database.

Milestone 7 is explicitly single-user and unauthenticated. A future PostgreSQL
migration should preserve the API, service, repository, and typed model
boundaries; it will require a PostgreSQL async driver, a PostgreSQL
`DATABASE_URL`, and review of migration/database-specific constraints. No
PostgreSQL server or driver is required now.

### Portfolio Accounting and Manual Prices

Migration `0002` adds `portfolio_transactions` and
`portfolio_price_marks`. To upgrade an existing Milestone 6 database without
removing its watchlist, stop FastAPI and run:

```powershell
Set-Location .\backend
.\.venv\Scripts\python.exe -m alembic upgrade head
```

The ledger uses weighted-average cost and replays transactions by trade date,
then creation timestamp, then ID. A buy adds `quantity × price + fees` to open
cost basis. A sale removes the sold quantity's proportional average cost and
calculates realized gain/loss as `quantity × sale price - fees - removed cost`.
A full sale removes any final rounding remainder. Backend calculations use
`Decimal`; stored money and quantity inputs use eight decimal places, while
reported average cost retains twelve decimal places. Future trade dates are
rejected using the current UTC date.

Short selling is not supported. A create, edit, or delete that would make the
chronological ledger negative returns a stable `409 portfolio_ledger_conflict`
and is rolled back. Closed positions disappear from the open-position list,
while their transactions and realized result remain in history and totals.

Current prices are user-entered `MANUAL` marks, not live or automatically
refreshed quotes. The application never substitutes a transaction price for a
missing mark. An unmarked position still reports its quantity and cost basis,
but its market value and unrealized values are explicitly unavailable. If even
one open position is unmarked, complete portfolio market value and unrealized
totals are `null`; marked subtotals and coverage counts remain available but
are not presented as the complete portfolio.

Everything in this milestone runs locally using free software and free SEC
data. There is no paid API, hosted service, brokerage connection, or live-price
dependency.

### Manual Persistence Check

1. Start FastAPI and Next.js in the order above.
2. Search for `MSFT`, open the Microsoft research page, and choose **Add to watchlist**.
3. Open `/watchlist` and confirm Microsoft appears.
4. Stop FastAPI, restart it without changing `DATABASE_URL`, and refresh `/watchlist`.
5. Confirm Microsoft remains, then remove it and verify the empty state.
6. Open `/portfolio`, record a buy, add a manual price, restart FastAPI, and
   confirm the transaction, calculated position, and manual mark remain.

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
mockable transport. Milestone 6 adds `SQLAlchemy==2.0.51`, `alembic==1.18.5`,
and `aiosqlite==0.22.1`. Milestone 7 adds no backend or frontend dependency.

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
- [x] Milestone 6: local SQLite persistence and a real watchlist
- [x] Milestone 7: persistent portfolio transactions and position intelligence
- [ ] Market-data integration
- [ ] Deeper fundamental analysis and SEC filing-document retrieval
- [ ] Thesis tracking and evidence comparison
- [ ] Valuation scenarios and local AI-assisted analysis
