"""Independent weighted-average portfolio accounting tests."""

from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from app.services.portfolio_accounting import (
    LedgerEntry,
    LedgerViolation,
    replay_ledger,
)


def entry(
    transaction_id: int,
    side: str,
    quantity: str,
    price: str,
    *,
    fees: str = "0",
    trade_date: date = date(2026, 1, 2),
    ticker: str = "MSFT",
) -> LedgerEntry:
    return LedgerEntry(
        id=transaction_id,
        ticker=ticker,
        company_name="MICROSOFT CORP",
        cik="0000789019",
        side=side,
        trade_date=trade_date,
        quantity=Decimal(quantity),
        price_per_share=Decimal(price),
        fees=Decimal(fees),
        created_at=datetime(2026, 1, transaction_id, tzinfo=timezone.utc),
    )


def test_multiple_buys_use_weighted_average_cost_and_fees() -> None:
    ledger = replay_ledger(
        [
            entry(1, "BUY", "10", "100", fees="5"),
            entry(2, "BUY", "5", "120", fees="5"),
        ]
    )
    position = ledger.positions["MSFT"]

    assert position.quantity == Decimal("15")
    assert position.open_cost_basis == Decimal("1610.00000000")
    assert position.average_cost == Decimal("107.333333333333")


def test_partial_sale_removes_proportional_basis_and_calculates_gain() -> None:
    ledger = replay_ledger(
        [
            entry(1, "BUY", "10", "100", fees="5"),
            entry(2, "BUY", "5", "120", fees="5"),
            entry(3, "SELL", "3", "150", fees="3"),
        ]
    )
    position = ledger.positions["MSFT"]

    assert position.quantity == Decimal("12")
    assert position.open_cost_basis == Decimal("1288.00000000")
    assert position.realized_gain_loss == Decimal("125.00000000")
    assert ledger.realized_gain_loss == Decimal("125.00000000")


def test_full_sale_closes_position_without_rounding_residue() -> None:
    ledger = replay_ledger(
        [
            entry(1, "BUY", "3", "10", fees="1"),
            entry(2, "SELL", "3", "12", fees="1"),
        ]
    )
    position = ledger.positions["MSFT"]

    assert position.quantity == Decimal("0")
    assert position.open_cost_basis == Decimal("0")
    assert position.realized_gain_loss == Decimal("4.00000000")


def test_multiple_sales_accumulate_realized_loss() -> None:
    ledger = replay_ledger(
        [
            entry(1, "BUY", "10", "20"),
            entry(2, "SELL", "4", "18", fees="2"),
            entry(3, "SELL", "2", "19", fees="1"),
        ]
    )

    assert ledger.positions["MSFT"].quantity == Decimal("4")
    assert ledger.positions["MSFT"].open_cost_basis == Decimal("80.00000000")
    assert ledger.realized_gain_loss == Decimal("-13.00000000")


def test_replay_uses_trade_date_created_at_and_id_order() -> None:
    later_buy = entry(
        2,
        "BUY",
        "2",
        "10",
        trade_date=date(2026, 1, 2),
    )
    earlier_buy = entry(
        1,
        "BUY",
        "1",
        "10",
        trade_date=date(2026, 1, 1),
    )
    sale = entry(
        3,
        "SELL",
        "3",
        "12",
        trade_date=date(2026, 1, 3),
    )

    ledger = replay_ledger([sale, later_buy, earlier_buy])

    assert ledger.positions["MSFT"].quantity == Decimal("0")
    assert ledger.realized_gain_loss == Decimal("6.00000000")


def test_oversell_reports_available_quantity_at_failure_point() -> None:
    with pytest.raises(LedgerViolation) as raised:
        replay_ledger(
            [
                entry(1, "BUY", "2", "10"),
                entry(2, "SELL", "3", "12"),
            ]
        )

    assert raised.value.available == Decimal("2")
