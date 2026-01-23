from __future__ import annotations


def american_to_decimal(american_odds: int) -> float:
    """Convert American odds to decimal odds."""
    if american_odds == 0:
        raise ValueError("American odds cannot be zero.")
    if american_odds > 0:
        return 1 + (american_odds / 100)
    return 1 + (100 / abs(american_odds))


def decimal_to_american(decimal_odds: float) -> int:
    """Convert decimal odds to American odds."""
    if decimal_odds <= 1:
        raise ValueError("Decimal odds must be greater than 1.")
    if decimal_odds >= 2:
        return int(round((decimal_odds - 1) * 100))
    return int(round(-100 / (decimal_odds - 1)))


def implied_prob_from_decimal(decimal_odds: float) -> float:
    """Convert decimal odds to implied probability (0-1)."""
    if decimal_odds <= 0:
        raise ValueError("Decimal odds must be positive.")
    return 1 / decimal_odds


def implied_prob_from_american(american_odds: int) -> float:
    """Convert American odds to implied probability (0-1)."""
    if american_odds == 0:
        raise ValueError("American odds cannot be zero.")
    if american_odds > 0:
        return 100 / (american_odds + 100)
    return abs(american_odds) / (abs(american_odds) + 100)


def implied_prob_to_decimal(implied_prob: float) -> float:
    """Convert implied probability (0-1) to decimal odds."""
    if implied_prob <= 0 or implied_prob >= 1:
        raise ValueError("Implied probability must be between 0 and 1.")
    return 1 / implied_prob
