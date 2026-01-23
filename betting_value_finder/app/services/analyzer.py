from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from app.services.normalizer import (
    decimal_to_american,
    implied_prob_from_american,
    implied_prob_to_decimal,
)


@dataclass(frozen=True)
class MarketOdds:
    bookmaker: str
    market_type: str
    home_price: int
    away_price: int


def detect_arbitrage(
    odds: Iterable[MarketOdds],
    min_profit_percent: float,
) -> list[dict]:
    """Detect arbitrage opportunities for head-to-head style markets."""

    opportunities: list[dict] = []
    grouped: dict[str, list[MarketOdds]] = defaultdict(list)
    for entry in odds:
        grouped[entry.market_type].append(entry)

    for market_type, market_odds in grouped.items():
        for home in market_odds:
            for away in market_odds:
                if home.bookmaker == away.bookmaker:
                    continue
                prob_home = implied_prob_from_american(home.home_price)
                prob_away = implied_prob_from_american(away.away_price)
                total_prob = prob_home + prob_away
                if total_prob >= 1:
                    continue
                profit = (1 - total_prob) * 100
                if profit < min_profit_percent:
                    continue
                opportunities.append(
                    {
                        "market_type": market_type,
                        "profit_percentage": round(profit, 2),
                        "bet_details": {
                            "home": {
                                "bookmaker": home.bookmaker,
                                "price": home.home_price,
                            },
                            "away": {
                                "bookmaker": away.bookmaker,
                                "price": away.away_price,
                            },
                        },
                    }
                )
    return opportunities


def detect_value_bets(
    odds: Iterable[MarketOdds],
    min_edge_percent: float,
) -> list[dict]:
    """Detect value bets by comparing consensus implied probability."""

    entries: list[dict] = []
    for entry in odds:
        entries.append(
            {
                "bookmaker": entry.bookmaker,
                "market_type": entry.market_type,
                "side": "home",
                "american_price": entry.home_price,
                "implied_prob": implied_prob_from_american(entry.home_price),
            }
        )
        entries.append(
            {
                "bookmaker": entry.bookmaker,
                "market_type": entry.market_type,
                "side": "away",
                "american_price": entry.away_price,
                "implied_prob": implied_prob_from_american(entry.away_price),
            }
        )

    if not entries:
        return []

    df = pd.DataFrame(entries)
    consensus = (
        df.groupby(["market_type", "side"])["implied_prob"].mean().reset_index()
    )
    merged = df.merge(consensus, on=["market_type", "side"], suffixes=("", "_consensus"))
    merged["edge"] = (merged["implied_prob_consensus"] - merged["implied_prob"]) * 100
    merged["consensus_price"] = merged["implied_prob_consensus"].apply(
        lambda prob: decimal_to_american(implied_prob_to_decimal(prob))
    )

    value_bets: list[dict] = []
    for _, row in merged.iterrows():
        if row["edge"] < min_edge_percent:
            continue
        value_bets.append(
            {
                "bookmaker": row["bookmaker"],
                "market_type": row["market_type"],
                "side": row["side"],
                "edge_percentage": round(row["edge"], 2),
                "consensus_price": int(row["consensus_price"]),
                "book_price": row["american_price"],
            }
        )

    return value_bets
