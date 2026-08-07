"""Pure Decimal-based weighted-average portfolio accounting."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_EVEN

MONEY_QUANTUM = Decimal("0.00000001")
AVERAGE_COST_QUANTUM = Decimal("0.000000000001")
PERCENT_QUANTUM = Decimal("0.000001")
ZERO = Decimal("0")


def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_EVEN)


def quantize_average(value: Decimal) -> Decimal:
    return value.quantize(AVERAGE_COST_QUANTUM, rounding=ROUND_HALF_EVEN)


def quantize_percent(value: Decimal) -> Decimal:
    return value.quantize(PERCENT_QUANTUM, rounding=ROUND_HALF_EVEN)


@dataclass(frozen=True)
class LedgerEntry:
    id: int
    ticker: str
    company_name: str
    cik: str
    side: str
    trade_date: date
    quantity: Decimal
    price_per_share: Decimal
    fees: Decimal
    created_at: datetime


@dataclass(frozen=True)
class AccountedPosition:
    ticker: str
    company_name: str
    cik: str
    quantity: Decimal
    open_cost_basis: Decimal
    average_cost: Decimal
    realized_gain_loss: Decimal


@dataclass(frozen=True)
class PortfolioLedger:
    positions: dict[str, AccountedPosition]
    realized_gain_loss: Decimal


class LedgerViolation(ValueError):
    """A transaction would make holdings negative in chronological order."""

    def __init__(self, entry: LedgerEntry, available: Decimal) -> None:
        self.entry = entry
        self.available = available
        super().__init__(
            f"{entry.ticker} sell quantity {entry.quantity} exceeds {available}."
        )


@dataclass
class _MutablePosition:
    ticker: str
    company_name: str
    cik: str
    quantity: Decimal = ZERO
    open_cost_basis: Decimal = ZERO
    realized_gain_loss: Decimal = ZERO


def replay_ledger(entries: list[LedgerEntry]) -> PortfolioLedger:
    """Replay trades deterministically using weighted-average cost."""

    ordered = sorted(
        entries,
        key=lambda entry: (entry.trade_date, entry.created_at, entry.id),
    )
    states: dict[str, _MutablePosition] = {}

    for entry in ordered:
        state = states.setdefault(
            entry.ticker,
            _MutablePosition(entry.ticker, entry.company_name, entry.cik),
        )

        if entry.side == "BUY":
            purchase_cost = quantize_money(
                entry.quantity * entry.price_per_share + entry.fees
            )
            state.quantity += entry.quantity
            state.open_cost_basis = quantize_money(
                state.open_cost_basis + purchase_cost
            )
            continue

        if entry.quantity > state.quantity:
            raise LedgerViolation(entry, state.quantity)

        if entry.quantity == state.quantity:
            removed_cost_basis = state.open_cost_basis
        else:
            removed_cost_basis = quantize_money(
                state.open_cost_basis * entry.quantity / state.quantity
            )

        proceeds = quantize_money(
            entry.quantity * entry.price_per_share - entry.fees
        )
        state.realized_gain_loss = quantize_money(
            state.realized_gain_loss + proceeds - removed_cost_basis
        )
        state.quantity -= entry.quantity
        state.open_cost_basis = quantize_money(
            state.open_cost_basis - removed_cost_basis
        )

        if state.quantity == ZERO:
            state.open_cost_basis = ZERO

    positions: dict[str, AccountedPosition] = {}
    total_realized = ZERO
    for ticker, state in states.items():
        total_realized = quantize_money(
            total_realized + state.realized_gain_loss
        )
        average_cost = (
            quantize_average(state.open_cost_basis / state.quantity)
            if state.quantity > ZERO
            else ZERO
        )
        positions[ticker] = AccountedPosition(
            ticker=ticker,
            company_name=state.company_name,
            cik=state.cik,
            quantity=state.quantity,
            open_cost_basis=state.open_cost_basis,
            average_cost=average_cost,
            realized_gain_loss=state.realized_gain_loss,
        )

    return PortfolioLedger(
        positions=positions,
        realized_gain_loss=total_realized,
    )
