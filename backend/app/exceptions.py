"""Predictable application exceptions exposed through the HTTP API."""


class ApplicationError(Exception):
    """Base exception carrying a stable public error contract."""

    status_code = 500
    code = "internal_error"
    default_message = "The request could not be completed."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class InvalidQueryError(ApplicationError):
    status_code = 422
    code = "invalid_query"
    default_message = "Search query must contain between 2 and 100 characters."


class InvalidTickerError(ApplicationError):
    status_code = 422
    code = "invalid_ticker"
    default_message = "Ticker must contain 1 to 10 letters, numbers, dots, or hyphens."


class InvalidFilingsQueryError(ApplicationError):
    status_code = 422
    code = "invalid_filings_query"
    default_message = "The filings query parameters are invalid."


class CompanyNotFoundError(ApplicationError):
    status_code = 404
    code = "company_not_found"
    default_message = "No SEC company was found for that ticker."


class SecConfigurationError(ApplicationError):
    status_code = 503
    code = "sec_configuration_missing"
    default_message = "SEC company data is not configured on this server."


class SecTimeoutError(ApplicationError):
    status_code = 504
    code = "sec_timeout"
    default_message = "The SEC data service did not respond before the timeout."


class SecRateLimitError(ApplicationError):
    status_code = 429
    code = "sec_rate_limited"
    default_message = "The SEC data service is temporarily rate limiting requests."


class SecUpstreamError(ApplicationError):
    status_code = 502
    code = "sec_upstream_failure"
    default_message = "The SEC data service is temporarily unavailable."


class SecMalformedResponseError(ApplicationError):
    status_code = 502
    code = "sec_malformed_response"
    default_message = "The SEC data service returned an unexpected response."


class WatchlistEntryExistsError(ApplicationError):
    status_code = 409
    code = "watchlist_entry_exists"
    default_message = "That company is already on the watchlist."


class WatchlistEntryNotFoundError(ApplicationError):
    status_code = 404
    code = "watchlist_entry_not_found"
    default_message = "That company is not on the watchlist."


class PortfolioTransactionNotFoundError(ApplicationError):
    status_code = 404
    code = "portfolio_transaction_not_found"
    default_message = "That portfolio transaction does not exist."


class PortfolioSecurityNotFoundError(ApplicationError):
    status_code = 404
    code = "portfolio_security_not_found"
    default_message = "That security does not exist in the portfolio ledger."


class PortfolioLedgerConflictError(ApplicationError):
    status_code = 409
    code = "portfolio_ledger_conflict"
    default_message = (
        "This change would sell more shares than are available at that point "
        "in the transaction history."
    )
