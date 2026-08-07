"""API, persistence, validation, and accounting tests for portfolios."""

from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.routes.companies import get_company_service
from app.main import app
from app.services.company_service import CompanyService

TRANSACTIONS_URL = "/api/v1/portfolio/transactions"
OVERVIEW_URL = "/api/v1/portfolio/overview"


class CountingCompanySource:
    def __init__(self, tickers: dict[str, Any]) -> None:
        self.tickers = tickers
        self.ticker_requests = 0

    async def get_company_tickers(self) -> dict[str, Any]:
        self.ticker_requests += 1
        return self.tickers


@pytest.fixture
def company_source(company_tickers_payload: dict[str, Any]) -> CountingCompanySource:
    return CountingCompanySource(company_tickers_payload)


@pytest.fixture
def company_service(company_source: CountingCompanySource) -> CompanyService:
    return CompanyService(company_source)


@pytest.fixture
def api_client(
    migrated_database_url: str,
    company_service: CompanyService,
) -> Iterator[TestClient]:
    del migrated_database_url
    app.dependency_overrides[get_company_service] = lambda: company_service
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def transaction_payload(
    *,
    ticker: str = "MSFT",
    side: str = "BUY",
    trade_date: str = "2026-01-02",
    quantity: str = "10",
    price: str = "100",
    fees: str = "0",
    notes: str | None = None,
) -> dict[str, str | None]:
    return {
        "ticker": ticker,
        "side": side,
        "trade_date": trade_date,
        "quantity": quantity,
        "price_per_share": price,
        "fees": fees,
        "notes": notes,
    }


def create_transaction(
    client: TestClient,
    **overrides: str,
) -> dict[str, Any]:
    response = client.post(
        TRANSACTIONS_URL,
        json=transaction_payload(**overrides),
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_empty_portfolio_has_explicit_complete_zero_totals(
    api_client: TestClient,
) -> None:
    response = api_client.get(OVERVIEW_URL)

    assert response.status_code == 200
    payload = response.json()
    assert payload["currency"] == "USD"
    assert payload["positions"] == []
    assert payload["totals"] == {
        "open_cost_basis": "0.00000000",
        "realized_gain_loss": "0.00000000",
        "market_value": "0.00000000",
        "marked_market_value": "0.00000000",
        "unrealized_gain_loss": "0.00000000",
        "marked_unrealized_gain_loss": "0.00000000",
        "open_position_count": 0,
        "transaction_count": 0,
        "marked_position_count": 0,
        "unmarked_position_count": 0,
        "manual_price_coverage_percent": None,
        "market_values_complete": True,
    }


def test_create_normalizes_ticker_and_stores_official_sec_identity(
    api_client: TestClient,
) -> None:
    payload = create_transaction(
        api_client,
        ticker=" msft ",
        quantity="0.12345678",
        price="1.23456789",
        fees="0.00000001",
        notes="  precision check  ",
    )

    expected_gross = (Decimal("0.12345678") * Decimal("1.23456789")).quantize(
        Decimal("0.00000001"),
        rounding=ROUND_HALF_EVEN,
    )
    assert payload["ticker"] == "MSFT"
    assert payload["cik"] == "0000789019"
    assert payload["company_name"] == "MICROSOFT CORP"
    assert payload["quantity"] == "0.12345678"
    assert payload["price_per_share"] == "1.23456789"
    assert payload["fees"] == "0.00000001"
    assert payload["gross_amount"] == format(expected_gross, "f")
    assert payload["notes"] == "precision check"


def test_existing_security_identity_avoids_repeated_sec_resolution(
    api_client: TestClient,
    company_source: CountingCompanySource,
) -> None:
    create_transaction(api_client, trade_date="2026-01-01")
    create_transaction(api_client, trade_date="2026-01-02")

    assert company_source.ticker_requests == 1


def test_transactions_are_newest_first_and_support_ticker_filtering(
    api_client: TestClient,
) -> None:
    first = create_transaction(api_client, trade_date="2026-01-01")
    second = create_transaction(api_client, trade_date="2026-01-02")
    uber = create_transaction(
        api_client,
        ticker="UBER",
        trade_date="2026-01-03",
    )

    all_ids = [
        item["id"]
        for item in api_client.get(TRANSACTIONS_URL).json()["transactions"]
    ]
    msft_ids = [
        item["id"]
        for item in api_client.get(
            TRANSACTIONS_URL,
            params={"ticker": "msft"},
        ).json()["transactions"]
    ]
    assert all_ids == [uber["id"], second["id"], first["id"]]
    assert msft_ids == [second["id"], first["id"]]


def test_weighted_average_partial_sale_and_manual_mark_scenario(
    api_client: TestClient,
) -> None:
    create_transaction(
        api_client,
        trade_date="2026-01-01",
        quantity="10",
        price="100",
        fees="5",
    )
    create_transaction(
        api_client,
        trade_date="2026-01-02",
        quantity="5",
        price="120",
        fees="5",
    )

    before_sale = api_client.get(OVERVIEW_URL).json()
    position = before_sale["positions"][0]
    assert position["quantity"] == "15.00000000"
    assert position["open_cost_basis"] == "1610.00000000"
    assert position["average_cost"] == "107.333333333333"
    assert position["realized_gain_loss"] == "0.00000000"

    create_transaction(
        api_client,
        side="SELL",
        trade_date="2026-01-03",
        quantity="3",
        price="150",
        fees="3",
    )
    mark = api_client.put(
        "/api/v1/portfolio/marks/msft",
        json={"price": "140", "as_of": "2026-01-04T15:30:00-06:00"},
    )
    assert mark.status_code == 200
    assert mark.json()["source"] == "MANUAL"
    assert mark.json()["as_of"] == "2026-01-04T21:30:00Z"

    overview = api_client.get(OVERVIEW_URL).json()
    position = overview["positions"][0]
    assert position["quantity"] == "12.00000000"
    assert position["open_cost_basis"] == "1288.00000000"
    assert position["realized_gain_loss"] == "125.00000000"
    assert position["market_value"] == "1680.00000000"
    assert position["unrealized_gain_loss"] == "392.00000000"
    assert position["price_as_of"] == "2026-01-04T21:30:00Z"
    assert overview["totals"]["market_value"] == "1680.00000000"
    assert overview["totals"]["unrealized_gain_loss"] == "392.00000000"


def test_full_sale_hides_position_but_preserves_realized_result(
    api_client: TestClient,
) -> None:
    create_transaction(api_client, quantity="2", price="10", fees="1")
    create_transaction(
        api_client,
        side="SELL",
        trade_date="2026-01-03",
        quantity="2",
        price="15",
        fees="1",
    )

    overview = api_client.get(OVERVIEW_URL).json()
    assert overview["positions"] == []
    assert overview["totals"]["realized_gain_loss"] == "8.00000000"
    assert overview["totals"]["transaction_count"] == 2


def test_partial_manual_price_coverage_never_claims_complete_totals(
    api_client: TestClient,
) -> None:
    create_transaction(api_client, ticker="MSFT", price="100")
    create_transaction(api_client, ticker="UBER", price="50")
    api_client.put("/api/v1/portfolio/marks/MSFT", json={"price": "120"})

    totals = api_client.get(OVERVIEW_URL).json()["totals"]
    assert totals["market_value"] is None
    assert totals["unrealized_gain_loss"] is None
    assert totals["marked_market_value"] == "1200.00000000"
    assert totals["marked_unrealized_gain_loss"] == "200.00000000"
    assert totals["marked_position_count"] == 1
    assert totals["unmarked_position_count"] == 1
    assert totals["manual_price_coverage_percent"] == "50.000000"
    assert totals["market_values_complete"] is False


def test_oversell_returns_stable_conflict(api_client: TestClient) -> None:
    create_transaction(api_client, quantity="12")
    response = api_client.post(
        TRANSACTIONS_URL,
        json=transaction_payload(
            side="SELL",
            trade_date="2026-01-03",
            quantity="12.00000001",
        ),
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "portfolio_ledger_conflict"
    assert len(api_client.get(TRANSACTIONS_URL).json()["transactions"]) == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("side", "HOLD"),
        ("quantity", "0"),
        ("quantity", "-1"),
        ("price_per_share", "0"),
        ("price_per_share", "-1"),
        ("fees", "-0.01"),
        ("trade_date", "not-a-date"),
    ],
)
def test_malformed_transaction_fields_return_stable_validation(
    api_client: TestClient,
    field: str,
    value: str,
) -> None:
    payload = transaction_payload()
    payload[field] = value
    response = api_client.post(TRANSACTIONS_URL, json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_future_trade_date_is_rejected(api_client: TestClient) -> None:
    future = (datetime.now(timezone.utc).date() + timedelta(days=1)).isoformat()
    response = api_client.post(
        TRANSACTIONS_URL,
        json=transaction_payload(trade_date=future),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_invalid_and_unknown_tickers_have_stable_errors(
    api_client: TestClient,
) -> None:
    invalid = api_client.post(
        TRANSACTIONS_URL,
        json=transaction_payload(ticker="not_valid!"),
    )
    unknown = api_client.post(
        TRANSACTIONS_URL,
        json=transaction_payload(ticker="ZZZZ"),
    )

    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "invalid_ticker"
    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "company_not_found"


def test_edit_updates_accounting_without_changing_identity(
    api_client: TestClient,
) -> None:
    transaction = create_transaction(api_client, quantity="10", price="100")
    response = api_client.patch(
        f"{TRANSACTIONS_URL}/{transaction['id']}",
        json={"quantity": "8", "price_per_share": "110", "fees": "2"},
    )

    assert response.status_code == 200
    assert response.json()["ticker"] == "MSFT"
    assert response.json()["cik"] == "0000789019"
    position = api_client.get(OVERVIEW_URL).json()["positions"][0]
    assert position["quantity"] == "8.00000000"
    assert position["open_cost_basis"] == "882.00000000"


def test_edit_that_invalidates_later_sell_rolls_back(api_client: TestClient) -> None:
    buy = create_transaction(
        api_client,
        trade_date="2026-01-01",
        quantity="10",
    )
    create_transaction(
        api_client,
        side="SELL",
        trade_date="2026-01-02",
        quantity="8",
    )

    response = api_client.patch(
        f"{TRANSACTIONS_URL}/{buy['id']}",
        json={"quantity": "5"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "portfolio_ledger_conflict"
    assert api_client.get(OVERVIEW_URL).json()["positions"][0]["quantity"] == "2.00000000"


def test_delete_replays_ledger_and_rejects_invalid_history(
    api_client: TestClient,
) -> None:
    first_buy = create_transaction(
        api_client,
        trade_date="2026-01-01",
        quantity="10",
    )
    second_buy = create_transaction(
        api_client,
        trade_date="2026-01-02",
        quantity="3",
    )
    create_transaction(
        api_client,
        side="SELL",
        trade_date="2026-01-03",
        quantity="8",
    )

    conflict = api_client.delete(f"{TRANSACTIONS_URL}/{first_buy['id']}")
    deleted = api_client.delete(f"{TRANSACTIONS_URL}/{second_buy['id']}")

    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "portfolio_ledger_conflict"
    assert deleted.status_code == 200
    assert deleted.json() == {
        "transaction_id": second_buy["id"],
        "deleted": True,
    }
    assert api_client.get(OVERVIEW_URL).json()["positions"][0]["quantity"] == "2.00000000"


def test_missing_transaction_and_unknown_mark_return_stable_not_found(
    api_client: TestClient,
) -> None:
    missing_edit = api_client.patch(
        f"{TRANSACTIONS_URL}/999",
        json={"fees": "1"},
    )
    missing_delete = api_client.delete(f"{TRANSACTIONS_URL}/999")
    unknown_mark = api_client.put(
        "/api/v1/portfolio/marks/MSFT",
        json={"price": "100"},
    )

    assert missing_edit.status_code == 404
    assert missing_delete.status_code == 404
    assert unknown_mark.status_code == 404
    assert missing_edit.json()["error"]["code"] == "portfolio_transaction_not_found"
    assert unknown_mark.json()["error"]["code"] == "portfolio_security_not_found"


def test_naive_mark_timestamp_and_invalid_mark_price_are_rejected(
    api_client: TestClient,
) -> None:
    create_transaction(api_client)
    naive = api_client.put(
        "/api/v1/portfolio/marks/MSFT",
        json={"price": "100", "as_of": "2026-01-03T12:00:00"},
    )
    negative = api_client.put(
        "/api/v1/portfolio/marks/MSFT",
        json={"price": "-1"},
    )

    assert naive.status_code == 422
    assert negative.status_code == 422


def test_portfolio_persists_across_application_lifespans(
    migrated_database_url: str,
    company_service: CompanyService,
) -> None:
    del migrated_database_url
    app.dependency_overrides[get_company_service] = lambda: company_service
    try:
        with TestClient(app) as first_client:
            transaction = create_transaction(first_client, quantity="4")
            assert first_client.put(
                "/api/v1/portfolio/marks/MSFT",
                json={"price": "125"},
            ).status_code == 200

        with TestClient(app) as restarted_client:
            overview = restarted_client.get(OVERVIEW_URL).json()
            history = restarted_client.get(TRANSACTIONS_URL).json()
            assert overview["positions"][0]["quantity"] == "4.00000000"
            assert overview["positions"][0]["manual_price"] == "125.00000000"
            assert history["transactions"][0]["id"] == transaction["id"]
    finally:
        app.dependency_overrides.clear()


def test_portfolio_cors_supports_patch_and_put(api_client: TestClient) -> None:
    for method in ("PATCH", "PUT"):
        response = api_client.options(
            TRANSACTIONS_URL,
            headers={
                "Origin": "http://127.0.0.1:3000",
                "Access-Control-Request-Method": method,
                "Access-Control-Request-Headers": "content-type",
            },
        )
        assert response.status_code == 200
        assert method in response.headers["access-control-allow-methods"]
