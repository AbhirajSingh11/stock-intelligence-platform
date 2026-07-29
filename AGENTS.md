# Stock Intelligence Platform — Project Instructions

## Product Purpose

Build a stock research and portfolio intelligence platform for a long-term
investor. The product should eventually support:

- a stock watchlist and historical prices;
- transactions, positions, and portfolio returns;
- revenue, margin, cash-flow, and debt analysis;
- SEC EDGAR 10-K, 10-Q, and 8-K retrieval;
- an investment thesis for each stock;
- comparison of new evidence with the original thesis;
- valuation scenarios; and
- local AI-assisted filing analysis.

## Required Technology

- Frontend: Next.js, TypeScript, and Tailwind CSS.
- Backend: Python and FastAPI.
- Database: PostgreSQL later. Do not require a database server during the
  initial milestones.
- Data sources: free SEC EDGAR APIs and a free market-data source.
- Development environment: Windows PowerShell and VS Code.
- Deployment is out of scope until explicitly requested.
- The project must remain completely free. Do not introduce paid APIs,
  paid services, or a required paid plan.

## Visual Direction

Use a professional, dark institutional research-terminal interface:

- charcoal or navy backgrounds;
- crisp white typography;
- emerald for positive values;
- amber for risk and warning states;
- dense but readable financial layouts; and
- no gradients.

## Working Agreement

- Work in small, explicit milestones. Do not build the entire application at
  once.
- Before each milestone, explain its scope and any meaningful architectural
  decisions.
- Explain every command and each important file in language suitable for a
  developer learning the stack.
- After every milestone, run appropriate validation and explain the results.
- Do not make major architectural decisions silently.
- Prefer clean, production-quality code over tutorial shortcuts.
- Do not proceed beyond the milestone requested by the user.
- Keep credentials and local secrets out of version control. Document new
  environment variables in an example environment file when introduced.
- Prefer PowerShell-compatible commands in project documentation.

## Current Repository Shape

- `frontend/` contains the Next.js application.
- `backend/` contains the FastAPI application and its tests.
- Root-level files document and coordinate the two applications.

